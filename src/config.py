import os
import platform
from pathlib import Path

class Config:
    def __init__(self):
        # Get project root directory (your specific path)
        self.project_root = Path("/Volumes/samsungT5/my_projects/jarvis").absolute()
        
        # Platform-specific settings
        self.is_mac = platform.system() == "Darwin"
        self.is_windows = platform.system() == "Windows"
        
        # Model paths on your external drive
        self.models_dir = self.project_root / "models"
        self.whisper_dir = self.models_dir / "mlx-whisper"
        self.llm_dir = self.models_dir / "mistral-7b"
        self.tts_dir = self.models_dir / "cosyvoice2" / "models"
        
        # Audio settings
        self.audio_sample_rate = 16000
        self.chunk_duration = 0.5  # seconds
        
        # Performance settings for external drive
        self.use_streaming = True
        self.max_file_cache_size = 100 * 1024 * 1024  # 100MB cache limit
        
        # System commands (cross-platform)
        self.music_apps = self._get_music_apps()
        
        # Wake word settings
        self.wake_word = "jarvis"
        self.min_confidence = 0.6
        
        # External drive optimization
        self.use_memory_cache = True
        self.max_cache_files = 10
    
    def _get_music_apps(self):
        """Get platform-specific music app paths"""
        if self.is_mac:
            return {
                "spotify": "/Applications/Spotify.app",
                "apple_music": "/System/Applications/Music.app",
                "browser": "open -a 'Google Chrome' https://music.youtube.com"
            }
        elif self.is_windows:
            return {
                "spotify": "C:\\Program Files\\Spotify\\Spotify.exe",
                "apple_music": "C:\\Program Files\\WindowsApps\\AppleInc.AppleMusic_*\\AppleMusic.exe",
                "browser": "start chrome https://music.youtube.com"
            }
        return {}
    
    def get_absolute_path(self, relative_path):
        """Convert relative path to absolute path on external drive"""
        return str(self.project_root / relative_path)
    
    def validate_paths(self):
        """Validate all required paths exist"""
        paths = [
            self.whisper_dir,
            self.llm_dir,
            self.tts_dir,
            self.models_dir / "mlx-cache"
        ]
        
        for path in paths:
            if not path.exists():
                print(f"❌ Warning: Path does not exist: {path}")
                path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created directory: {path}")
        
        # Set environment variables for external drive
        os.environ["MLX_CACHE_DIR"] = str(self.models_dir / "mlx-cache")
        os.environ["COSYVOICE_MODEL_DIR"] = str(self.tts_dir)

# Create global config instance
CONFIG = Config()
CONFIG.validate_paths()

print(f"✅ Configuration loaded for project root: {CONFIG.project_root}")
print(f"📂 Models directory: {CONFIG.models_dir}")