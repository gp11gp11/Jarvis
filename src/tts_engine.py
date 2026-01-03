import numpy as np
import sounddevice as sd
import sys
import os
import subprocess
import threading
import queue
import time
import warnings
from pathlib import Path
from config import CONFIG

# Add CosyVoice2 to Python path
sys.path.insert(0, str(CONFIG.project_root / "models" / "cosyvoice2"))

try:
    from cosyvoice.cli.cosyvoice import CosyVoice
    from cosyvoice.utils.file_utils import load_wav
    COSYVOICE_AVAILABLE = True
except ImportError as e:
    print(f"❌ CosyVoice import error: {e}")
    print("💡 Make sure you cloned the CosyVoice2 repository correctly")
    print(f"   Expected path: {CONFIG.project_root / 'models' / 'cosyvoice2'}")
    COSYVOICE_AVAILABLE = False

class CosyVoiceTTS:
    def __init__(self):
        self.config = CONFIG
        self.model = None
        self.audio_queue = queue.Queue()
        self.is_speaking = False
        self.stream = None
        
        # Suppress warnings for cleaner output
        warnings.filterwarnings("ignore", category=UserWarning)
        
        if COSYVOICE_AVAILABLE:
            self.load_model()
        else:
            print("❌ CosyVoice2 not available. Using fallback TTS.")
    
    def load_model(self):
        """Load CosyVoice2-0.5B model from your external drive"""
        try:
            model_path = self.config.tts_dir / "cosyvoice2-0.5b"
            
            if not model_path.exists():
                print(f"❌ Model path does not exist: {model_path}")
                print("💡 Please run the model download command from install.sh")
                return False
            
            print(f"🗣️ Loading CosyVoice2-0.5B from: {model_path}")
            print("   ⏰ This may take 1-2 minutes on first load...")
            
            start_time = time.time()
            
            # Set environment variables for external drive access
            os.environ["COSYVOICE_MODEL_DIR"] = str(self.config.tts_dir)
            
            # Load model with your external drive path
            self.model = CosyVoice(str(model_path))
            
            load_time = time.time() - start_time
            print(f"✅ CosyVoice2-0.5B model loaded successfully in {load_time:.2f}s!")
            return True
        except Exception as e:
            print(f"❌ Error loading CosyVoice model: {e}")
            print("💡 Troubleshooting steps:")
            print("   • Check if the model was downloaded correctly")
            print("   • Verify the path exists: ls -la", self.config.tts_dir)
            print("   • Ensure you have enough disk space on your Samsung T5")
            return False
    
    def speak(self, text, stream=True):
        """Generate and play speech with low latency from external drive"""
        if not text.strip() or self.is_speaking:
            return
        
        if not COSYVOICE_AVAILABLE:
            self._fallback_tts(text)
            return
        
        self.is_speaking = True
        
        def generate_and_play():
            try:
                print(f"🗣️ Generating speech for: '{text[:50]}...'")
                start_time = time.time()
                
                # Generate speech with streaming from external drive
                if stream and hasattr(self.model, 'inference_stream'):
                    first_chunk_time = None
                    for i, chunk in enumerate(self.model.inference_stream(text)):
                        if i == 0:
                            first_chunk_time = time.time()
                            print(f"⏱️ First audio chunk ready in {first_chunk_time - start_time:.2f}s")
                        
                        if 'tts_speech' in chunk:
                            audio_chunk = chunk['tts_speech'].numpy()
                            self._play_audio_chunk(audio_chunk)
                else:
                    result = self.model.inference(text)
                    if 'tts_speech' in result:
                        audio = result['tts_speech'].numpy()
                        self._play_audio(audio)
                
                total_time = time.time() - start_time
                print(f"✅ Speech generation completed in {total_time:.2f}s")
                
            except Exception as e:
                print(f"❌ TTS generation error: {e}")
                print("💡 TTS troubleshooting tips:")
                print("   • Check if model files are corrupted")
                print("   • Ensure you have enough RAM (64GB should be sufficient)")
                print("   • Try restarting the application")
                self._fallback_tts(text)
            finally:
                self.is_speaking = False
        
        # Start in separate thread to avoid blocking
        threading.Thread(
            target=generate_and_play,
            daemon=True,
            name="TTSThread"
        ).start()
    
    def _play_audio_chunk(self, audio_chunk):
        """Play audio chunk with minimal latency"""
        try:
            # Ensure proper audio format
            if audio_chunk.dtype != np.float32:
                audio_chunk = audio_chunk.astype(np.float32)
            
            # Normalize audio to prevent clipping
            max_val = np.max(np.abs(audio_chunk))
            if max_val > 1.0:
                audio_chunk = audio_chunk / max_val
            
            # Play with low latency
            sd.play(audio_chunk, 24000, blocking=False)
            sd.wait()
        except Exception as e:
            print(f"❌ Audio playback error: {e}")
    
    def _play_audio(self, audio):
        """Play full audio"""
        try:
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)
            
            # Normalize audio
            max_val = np.max(np.abs(audio))
            if max_val > 1.0:
                audio = audio / max_val
            
            sd.play(audio, 24000)
            sd.wait()
        except Exception as e:
            print(f"❌ Full audio playback error: {e}")
    
    def _fallback_tts(self, text):
        """Simple fallback TTS using macOS 'say' command"""
        print(f"🔤 Fallback TTS: {text}")
        self.is_speaking = True
        
        def speak_system():
            try:
                # Use macOS system voice
                subprocess.run(["say", text])
            except Exception as e:
                print(f"❌ System TTS error: {e}")
            finally:
                self.is_speaking = False
                
        threading.Thread(target=speak_system, daemon=True).start()
    
    def is_busy(self):
        """Check if TTS is currently speaking"""
        return self.is_speaking