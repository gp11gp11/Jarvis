#!/usr/bin/env python3
"""
config.py - Configuration for Jarvis AI
"""

import os
import platform
from pathlib import Path


class Config:
    """Holds all configuration settings for Jarvis."""
    
    def __init__(self):
        """Initialize configuration with default values."""
        # Define where our project lives on the computer
        self.project_root = Path("/Volumes/samsungT5/my_projects/jarvis").absolute()
        
        # Detect which operating system we're running on
        self.is_mac = platform.system() == "Darwin"
        self.is_windows = platform.system() == "Windows"
        self.is_linux = platform.system() == "Linux"
        
        # Paths to our AI models (stored on external drive)
        self.models_dir = self.project_root / "models"
        self.whisper_model = "mlx-community/whisper-large-v3-turbo"
        self.llm_dir = self.models_dir / "mistral-7b"
        self.tts_dir = self.models_dir / "cosyvoice2"
        
        # Audio settings for microphone input
        self.audio_sample_rate = 16000  # 16 kHz - standard for speech
        self.chunk_duration = 0.5       # Process audio every 0.5 seconds
        
        # Wake word - the word that activates Jarvis
        self.wake_word = "jarvis"
    
    def validate_paths(self):
        """Check if required directories exist, create if needed."""
        print(f"📂 Project root: {self.project_root}")
        
        # Create models directory if it doesn't exist
        if not self.models_dir.exists():
            self.models_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: {self.models_dir}")
        
        # Create MLX cache directory for downloaded models
        cache_dir = self.models_dir / "mlx-cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Set environment variable so MLX knows where to cache
        os.environ["MLX_CACHE_DIR"] = str(cache_dir)
        
        return True


# ============================================================
# CREATE GLOBAL CONFIG INSTANCE
# ============================================================
# This code runs when you do: from config import CONFIG
# It creates a single Config object that everyone shares

CONFIG = Config()
CONFIG.validate_paths()

# Print a welcome message
print("=" * 50)
print("✅ Jarvis Configuration Loaded!")
print(f"🖥️  Platform: {'Mac' if CONFIG.is_mac else 'Windows' if CONFIG.is_windows else 'Linux'}")
print(f"🎤 Sample rate: {CONFIG.audio_sample_rate} Hz")
print(f"🗣️  Wake word: '{CONFIG.wake_word}'")
print("=" * 50)
