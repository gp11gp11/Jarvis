import sys
import os
import time
import warnings
from pathlib import Path
from config import CONFIG

try:
    import mlx_lm
    from mlx_lm import load, generate
    MLX_AVAILABLE = True
except ImportError as e:
    print(f"❌ MLX import error: {e}")
    print("💡 Make sure you installed mlx-lm correctly")
    MLX_AVAILABLE = False

class MistralLLM:
    def __init__(self):
        self.config = CONFIG
        self.model = None
        self.tokenizer = None
        
        # Suppress MLX warnings for cleaner output
        warnings.filterwarnings("ignore", category=UserWarning, module="mlx")
        
        if MLX_AVAILABLE:
            self.load_model()
        else:
            print("❌ MLX not available. LLM functionality disabled.")
    
    def load_model(self):
        """Load quantized Mistral 7B model from your external drive"""
        try:
            model_path = self.config.llm_dir
            
            if not model_path.exists():
                print(f"❌ Model path does not exist: {model_path}")
                print("💡 Please run the model conversion command from install.sh")
                return False
            
            print(f"🧠 Loading Mistral 7B from: {model_path}")
            print("   ⏰ This may take 2-3 minutes on first load...")
            
            # Set MLX cache to external drive
            os.environ["MLX_CACHE_DIR"] = str(self.config.models_dir / "mlx-cache")
            
            # Load model from external drive
            start_time = time.time()
            self.model, self.tokenizer = load(
                str(model_path),
                tokenizer_config={"use_fast": True}
            )
            load_time = time.time() - start_time
            
            print(f"✅ Mistral 7B loaded successfully in {load_time:.2f}s!")
            return True
        except Exception as e:
            print(f"❌ Error loading Mistral model: {e}")
            print("💡 LLM troubleshooting tips:")
            print("   • Check if the model was converted correctly")
            print("   • Verify you have enough disk space on your Samsung T5")
            print("   • Ensure your M1 Max has enough memory (64GB should be sufficient)")
            print("   • Try running with smaller context: --max-tokens 128")
            return False
    
    def generate_response(self, prompt, context=None):
        """Generate response with low latency from external drive"""
        if not MLX_AVAILABLE or self.model is None:
            return "LLM not available. Please check model loading and try again."
        
        try:
            system_prompt = """You are JARVIS, a highly intelligent AI assistant. 
            Respond concisely and helpfully. For commands like playing music, ask for clarification about which app to use.
            Keep responses short and natural for voice interaction. Be direct and efficient."""
            
            full_prompt = f"<s>[INST] {system_prompt}\n\nUser: {prompt} [/INST]"
            
            if context:
                full_prompt = f"{context}\n{full_prompt}"
            
            print(f"💭 LLM Input: {prompt[:50]}...")
            start_time = time.time()
            
            # Generate response with streaming
            response = generate(
                self.model,
                self.tokenizer,
                prompt=full_prompt,
                max_tokens=128,
                temp=0.3,
                top_p=0.9,
                verbose=False
            )
            
            response_time = time.time() - start_time
            print(f"⚡ LLM Response time: {response_time:.2f}s")
            
            # Clean up response
            response = response.replace("<s>", "").replace("[/INST]", "").strip()
            if not response:
                response = "I'm here to help. What would you like me to do?"
            
            print(f"🤖 LLM Output: {response[:50]}...")
            
            return response
            
        except Exception as e:
            print(f"❌ LLM generation error: {e}")
            print("💡 LLM generation troubleshooting:")
            print("   • Check if model is still loading")
            print("   • Try simpler prompts")
            print("   • Ensure you have enough system resources")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def parse_action(self, text):
        """Parse action commands from LLM response"""
        if not text:
            return None
        
        action_map = {
            "play music": "ask_music_app",
            "open spotify": "open_spotify",
            "open apple music": "open_apple_music",
            "play in browser": "open_browser_music",
            "weather": "get_weather",
            "time": "get_time",
            "exit": "exit_system",
            "quit": "exit_system",
            "shutdown": "exit_system",
            "close": "exit_system"
        }
        
        text_lower = text.lower()
        for keyword, action in action_map.items():
            if keyword in text_lower:
                print(f"🔍 Action detected: '{keyword}' -> '{action}'")
                return action
        
        return None