import numpy as np
import sounddevice as sd
import librosa
import mlx_whisper
from config import CONFIG
import threading
import queue
import time
import os
import warnings

class MLXWhisperSTT:
    def __init__(self):
        self.config = CONFIG
        self.audio_queue = queue.Queue(maxsize=100)  # Limit queue size for external drive
        self.is_recording = False
        self.stream = None
        self.sample_rate = self.config.audio_sample_rate
        self.min_silence_duration = 0.3  # seconds
        self.last_speech_time = 0
        
        # Set MLX cache directory to your external drive
        os.environ["MLX_CACHE_DIR"] = str(self.config.models_dir / "mlx-cache")
        
        # Suppress MLX warnings for cleaner output
        warnings.filterwarnings("ignore", category=UserWarning, module="mlx")
        
        print(f"🎤 Initializing STT with model path: {self.config.whisper_dir}")
    
    def start_listening(self, callback):
        """Start continuous listening with streaming optimized for external drive"""
        self.is_recording = True
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio status: {status}")
            if not self.audio_queue.full():
                self.audio_queue.put(indata.copy())
        
        # Start audio stream with buffer size optimized for external storage
        buffer_size = int(self.sample_rate * self.config.chunk_duration)
        
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=audio_callback,
                blocksize=buffer_size,
                latency='low',
                dtype='float32'
            )
            self.stream.start()
            print("✅ Audio stream started successfully")
        except Exception as e:
            print(f"❌ Audio stream error: {e}")
            print("💡 Troubleshooting tips:")
            print("   • Check if microphone permissions are granted")
            print("   • Try running: sudo chmod a+rw /dev/dsp (if on Linux)")
            print("   • Ensure no other applications are using the microphone")
            return
        
        # Start processing thread
        threading.Thread(
            target=self._process_audio_stream, 
            args=(callback,),
            daemon=True,
            name="STTProcessor"
        ).start()
        print("🔄 STT processing thread started")
    
    def stop_listening(self):
        """Stop recording"""
        self.is_recording = False
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
                print("⏹️ Audio stream stopped")
            except:
                pass
    
    # Common Whisper hallucinations to filter out
    HALLUCINATION_PHRASES = {
        "thank you", "thanks for watching", "thanks for listening",
        "subscribe", "like and subscribe", "see you next time",
        "bye", "goodbye", "you", ".", "...", "thank you.",
        "thanks", "okay", "ok", "um", "uh", "hmm", "ah",
        "please subscribe", "thanks for watching.",
        "for more information", "visit www", "www.fema.org",
        "i'm sorry", "i don't know", "what", "the", "a", "it",
    }
    
    # Patterns that indicate hallucination (repetitive text)
    HALLUCINATION_PATTERNS = [
        "analyzed", "transcribed", "subtitled", "captioned",
        "copyright", "all rights reserved", "music", "applause",
    ]
    
    def _is_hallucination(self, text):
        """Check if transcription is a common Whisper hallucination"""
        clean = text.lower().strip().rstrip('.!?,')
        
        # Check exact matches
        if clean in self.HALLUCINATION_PHRASES or len(clean) < 3:
            return True
        
        # Check for repetitive patterns (hallucination indicator)
        words = clean.split()
        if len(words) >= 3:
            # Check if same word/phrase repeats
            for pattern in self.HALLUCINATION_PATTERNS:
                if pattern in clean:
                    return True
            # Check for word repetition
            if len(set(words)) <= len(words) // 2:
                return True  # Too many repeated words
        
        return False
    
    def _calculate_rms(self, audio_data):
        """Calculate RMS energy of audio"""
        return np.sqrt(np.mean(audio_data ** 2))
    
    def _process_audio_stream(self, callback):
        """Process audio chunks with external drive optimization"""
        buffer = []
        last_processed_time = 0
        min_processing_interval = 1.0  # seconds between processing
        # Thresholds based on observed ambient noise (Peak: 0.02-0.10, RMS: 0.006-0.04)
        silence_threshold = 0.12  # Peak threshold - above ambient noise
        rms_threshold = 0.045  # RMS threshold - above ambient noise
        debug_interval = 5.0  # Print debug info every 5 seconds
        last_debug_time = 0
        
        print("🎧 STT processing started - listening for wake word 'jarvis'")
        
        while self.is_recording:
            try:
                chunk = self.audio_queue.get(timeout=0.1)
                chunk = chunk.flatten()
                
                # Check for silence using both peak and RMS
                peak = np.max(np.abs(chunk))
                rms = self._calculate_rms(chunk)
                
                # Debug: print audio levels periodically
                current_time = time.time()
                if current_time - last_debug_time > debug_interval:
                    print(f"🔊 Audio levels - Peak: {peak:.4f}, RMS: {rms:.4f}")
                    last_debug_time = current_time
                
                # Only consider silence if BOTH peak AND rms are below thresholds
                if peak < silence_threshold and rms < rms_threshold:
                    if current_time - self.last_speech_time > self.min_silence_duration:
                        # Clear buffer during silence
                        buffer = []
                    continue
                
                self.last_speech_time = time.time()
                
                # Add to buffer
                buffer.extend(chunk)
                
                current_time = time.time()
                buffer_duration = len(buffer) / self.sample_rate
                
                # Process when buffer has enough data and minimum time has passed
                if buffer_duration >= 2.0 and (current_time - last_processed_time) >= min_processing_interval:
                    # Take only the last 2.5 seconds of audio
                    audio_data = np.array(buffer[-int(self.sample_rate * 2.5):])
                    
                    # Additional check: ensure audio has sufficient energy (very low threshold)
                    if self._calculate_rms(audio_data) < 0.003:
                        buffer = buffer[-int(self.sample_rate * 1.5):]
                        continue
                    
                    last_processed_time = current_time
                    
                    # Convert to 16-bit PCM for Whisper
                    audio_data = (audio_data * 32767).astype(np.int16)
                    
                    try:
                        # Transcribe with MLX-Whisper using your external drive model
                        start_time = time.time()
                        result = mlx_whisper.transcribe(
                            audio_data,
                            path_or_hf_repo='mlx-community/whisper-large-v3-turbo',
                            verbose=False
                        )
                        transcribe_time = time.time() - start_time
                        
                        if result["text"].strip():
                            clean_text = result["text"].strip()
                            
                            # Filter out hallucinations
                            if self._is_hallucination(clean_text):
                                continue
                            
                            print(f"📝 Transcribed: '{clean_text}' (time: {transcribe_time:.2f}s)")
                            
                            # Check for wake word
                            if self.config.wake_word in clean_text.lower():
                                callback(clean_text)
                            elif "exit" in clean_text.lower() or "quit" in clean_text.lower():
                                callback(clean_text)
                        
                    except Exception as e:
                        print(f"❌ STT transcription error: {e}")
                    
                    # Keep buffer manageable size
                    if len(buffer) > self.sample_rate * 5:  # 5 seconds max
                        buffer = buffer[-int(self.sample_rate * 3):]
                        
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ STT processing error: {e}")
                time.sleep(0.5)  # Prevent tight loop on errors
    
    def transcribe_file(self, file_path):
        """Transcribe audio file from external drive"""
        try:
            print(f"📂 Transcribing file: {file_path}")
            result = mlx_whisper.transcribe(
                file_path,
                path_or_hf_repo='mlx-community/whisper-large-v3-turbo',
                verbose=False
            )
            return result["text"].strip()
        except Exception as e:
            print(f"❌ File transcription error: {e}")
            return ""