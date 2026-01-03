#!/usr/bin/env python3
"""
Jarvis AI - Main Entry Point
Runs entirely from your Samsung T5 external drive
"""

import sys
import os
import time
import threading
import signal
from pathlib import Path
from config import CONFIG

# Add project directories to Python path
sys.path.insert(0, str(CONFIG.project_root / "src"))
sys.path.insert(0, str(CONFIG.project_root / "models" / "cosyvoice2"))

from stt_engine import MLXWhisperSTT
from llm_engine import MistralLLM
from tts_engine import CosyVoiceTTS
from action_executor import ActionExecutor

class JarvisAI:
    def __init__(self):
        print("🚀 Initializing Jarvis AI System from External Drive...")
        print(f"📂 Project Root: {CONFIG.project_root}")
        
        # Initialize components
        self.stt = MLXWhisperSTT()
        self.llm = MistralLLM()
        self.tts = CosyVoiceTTS()
        self.action_executor = ActionExecutor()
        
        self.is_active = True
        self.conversation_context = ""
        self.wake_word = CONFIG.wake_word
        
        # Set up signal handlers for clean shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("✅ System initialized successfully!")
    
    def signal_handler(self, signum, frame):
        """Handle system signals for clean shutdown"""
        print("\n⚠️  Received shutdown signal...")
        self.stop()
    
    def start(self):
        """Start the main Jarvis loop"""
        print("\n" + "="*60)
        print("🎙️  JARVIS AI IS NOW ACTIVE!")
        print("="*60)
        print(f"📍 Running from external drive: {CONFIG.project_root}")
        print(f"💡 Say '{self.wake_word}' to wake me up, or 'exit' to quit")
        print(f"💾 Samsung T5 Drive: /Volumes/samsungT5")
        print("="*60 + "\n")
        
        # Start continuous listening
        self.stt.start_listening(self.process_input)
        
        try:
            while self.is_active:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            print(f"❌ Main loop error: {e}")
            self.stop()
    
    def stop(self):
        """Stop Jarvis"""
        print("\n" + "="*60)
        print("🛑 SHUTTING DOWN JARVIS AI...")
        print("="*60)
        
        self.is_active = False
        self.stt.stop_listening()
        
        # Stop TTS if speaking
        if hasattr(self.tts, 'is_speaking') and self.tts.is_speaking:
            print("⏹️  Stopping current speech...")
            # Wait for TTS to finish
            time.sleep(2)
        
        # Cleanup resources
        print("🧹 Cleaning up resources...")
        if hasattr(self.tts, 'stream') and self.tts.stream:
            try:
                self.tts.stream.stop()
                self.tts.stream.close()
            except:
                pass
        
        print("✅ System shutdown complete.")
        sys.exit(0)
    
    def process_input(self, text):
        """Process user input through the pipeline"""
        if not text.strip() or not self.is_active:
            return
        
        # Convert to lowercase for wake word detection
        text_lower = text.lower().strip()
        
        print(f"\n👤 User: {text}")
        
        # Check for exit command first
        if any(cmd in text_lower for cmd in ["exit", "shutdown", "close"]):
            if text_lower in ["exit", "quit", "shutdown", "close"] or f"exit {self.wake_word}" in text_lower:
                self.tts.speak("Shutting down Jarvis. Goodbye!")
                threading.Timer(2.0, self.stop).start()
                return
        
        # Wake word variations (common STT errors)
        wake_words = [self.wake_word, "javis", "travis", "davis", "service", "harvest", "jarvis"]
        
        # Check if any wake word is present
        detected_wake_word = None
        for ww in wake_words:
            if ww in text_lower:
                detected_wake_word = ww
                break
        
        if not detected_wake_word:
            # Not addressed to Jarvis
            return
        
        # Remove wake word from command
        command = text_lower.replace(detected_wake_word, "").strip()
        
        # Clean up command
        if command.startswith(",") or command.startswith("."):
            command = command[1:].strip()
            
        if not command:
            self.tts.speak("Yes?")
            return
        
        print(f"🔧 Command: {command}")
        
        # Wait if TTS is still speaking
        while self.tts.is_busy():
            time.sleep(0.1)
        
        # Generate response using LLM
        start_time = time.time()
        response = self.llm.generate_response(command, self.conversation_context)
        llm_time = time.time() - start_time
        
        print(f"🤖 JARVIS: {response} (LLM time: {llm_time:.2f}s)")
        
        # Check if response contains an action command
        action = self.llm.parse_action(response)
        if action:
            print(f"⚡ Executing action: {action}")
            action_result = self.action_executor.execute_action(action)
            if action_result:
                response = action_result
                print(f"✅ Action result: {action_result}")
            
            # Handle exit action
            if action == "exit_system":
                threading.Timer(1.0, self.stop).start()
                return
        
        # Update conversation context (keep last 2 exchanges)
        self.conversation_context = f"User: {command}\nJARVIS: {response}"
        if len(self.conversation_context.split('\n')) > 4:
            self.conversation_context = '\n'.join(self.conversation_context.split('\n')[-4:])
        
        # Speak response with low latency
        self.tts.speak(response, stream=True)
    
    def test_pipeline(self):
        """Test the complete pipeline with a sample command"""
        print("\n" + "="*60)
        print("🧪 TESTING PIPELINE")
        print("="*60)
        
        test_command = "play some music"
        print(f"🔧 Test command: {test_command}")
        
        # Simulate STT output
        start_time = time.time()
        self.process_input(test_command)
        total_time = time.time() - start_time
        
        print(f"\n✅ Pipeline test completed in {total_time:.2f} seconds")
        print("="*60)
        
        # Wait for TTS to finish
        while self.tts.is_busy():
            time.sleep(0.1)

if __name__ == "__main__":
    try:
        # Initialize and start Jarvis
        jarvis = JarvisAI()
        
        # Run a quick test
        jarvis.test_pipeline()
        
        # Give user time to see test results
        time.sleep(2)
        
        # Start main loop
        jarvis.start()
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print("💡 Troubleshooting steps:")
        print("   • Check if all dependencies are installed")
        print("   • Verify model paths exist")
        print("   • Ensure your Samsung T5 drive is properly mounted")
        print(f"   • Project root: {CONFIG.project_root}")
        sys.exit(1)