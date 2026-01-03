import subprocess
import json
import os
import requests
from datetime import datetime
from config import CONFIG

class ActionExecutor:
    def __init__(self):
        self.config = CONFIG
    
    def execute_action(self, action, parameters=None):
        """Execute system actions based on LLM commands"""
        print(f"⚡ Executing action: {action}")
        
        if action == "ask_music_app":
            return "Would you like me to play music in your browser or open your music app?"
        
        elif action == "open_spotify":
            return self._open_app("spotify")
        
        elif action == "open_apple_music":
            return self._open_app("apple_music")
        
        elif action == "open_browser_music":
            return self._open_app("browser")
        
        elif action == "get_weather":
            return self._get_weather()
        
        elif action == "get_time":
            return self._get_time()
        
        elif action == "exit_system":
            return "Shutting down Jarvis. Goodbye!"
        
        return f"Command '{action}' executed successfully."
    
    def _open_app(self, app_name):
        """Open specified application"""
        print(f"🖥️ Opening app: {app_name}")
        
        if app_name in self.config.music_apps:
            try:
                cmd = self.config.music_apps[app_name]
                
                if app_name == "browser":
                    print(f"🌐 Opening browser with command: {cmd}")
                    subprocess.Popen(cmd, shell=True)
                    return f"Opening music in your browser..."
                else:
                    app_path = cmd
                    print(f"🎵 Opening music app: {app_path}")
                    if CONFIG.is_mac:
                        subprocess.Popen(["open", "-a", app_path])
                    elif CONFIG.is_windows:
                        subprocess.Popen([app_path])
                    return f"Opening {app_name.replace('_', ' ')}..."
            
            except Exception as e:
                error_msg = f"Error opening {app_name}: {str(e)}"
                print(f"❌ {error_msg}")
                return error_msg
        
        return f"App {app_name} not found in configuration."
    
    def _get_weather(self):
        """Get current weather (placeholder)"""
        print("🌤️ Getting weather information...")
        return "I can check the weather for you. Please specify your location or enable weather API integration."
    
    def _get_time(self):
        """Get current time"""
        print("⏰ Getting current time...")
        now = datetime.now()
        time_str = now.strftime('%I:%M %p')
        date_str = now.strftime('%B %d, %Y')
        return f"The current time is {time_str} on {date_str}."