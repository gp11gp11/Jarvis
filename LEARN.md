# 🎓 Jarvis AI - Learning Guide

This file documents every concept explained while building Jarvis from scratch.

---

# 📁 File: `config.py`

## Step 1: Shebang & Docstring

```python
#!/usr/bin/env python3
"""
config.py - Configuration for Jarvis AI
"""
```

### Line 1: `#!/usr/bin/env python3`
- Called a **"shebang"** (pronounced "sha-bang")
- Tells your computer: "Run this file using Python 3"
- On Mac/Linux, you can run the file directly: `./config.py` instead of `python3 config.py`
- It's optional but considered good practice

### Lines 2-4: `"""..."""`
- Called a **docstring** (documentation string)
- Triple quotes `"""` allow multi-line strings
- At the top of a file, it describes what the file does
- Tools like `help(config)` will show this text

---

## Step 2: Import Statements

```python
import os
import platform
from pathlib import Path
```

### `import os`
- `os` = Operating System
- Gives us tools to interact with your computer
- We'll use `os.environ` to set environment variables (global settings)
- Example: `os.environ["PATH"]` gets your system PATH

### `import platform`
- Lets us detect which OS is running (Mac, Windows, Linux)
- `platform.system()` returns:
  - `"Darwin"` for Mac
  - `"Windows"` for Windows
  - `"Linux"` for Linux
- We need this because file paths and apps differ between systems

### `from pathlib import Path`
- `pathlib` is Python's modern way to work with file paths
- Why not just use strings? Because:
  - Mac uses `/` (forward slash): `/Users/name/file.txt`
  - Windows uses `\` (backslash): `C:\Users\name\file.txt`
- `Path` handles this automatically!

**Example:**
```python
# Without pathlib (breaks on different OS):
path = "/Users/" + "name" + "/" + "file.txt"

# With pathlib (works everywhere):
path = Path("/Users") / "name" / "file.txt"
```

### Why `from pathlib import Path` instead of `import pathlib`?

**Option 1: `import pathlib`**
```python
import pathlib
path = pathlib.Path("/Volumes/samsungT5")  # Must use prefix
```

**Option 2: `from pathlib import Path`**
```python
from pathlib import Path
path = Path("/Volumes/samsungT5")  # Shorter, cleaner
```

We use Option 2 because:
- We only need `Path` from pathlib, not other things
- It makes code shorter and cleaner
- Same pattern: `import os` keeps `os.environ`, but if we only needed `environ`, we'd use `from os import environ`

---

## Step 3: Creating a Class

```python
class Config:
    """Holds all configuration settings for Jarvis."""
    
    def __init__(self):
        """Initialize configuration with default values."""
        pass
```

### `class Config:`
- A **class** is like a blueprint for creating objects
- Think of it like a cookie cutter:
  - The class = the cutter shape
  - Objects = the cookies you make
- Naming convention: Classes use `PascalCase` (each word capitalized)

**Another way to think about it - Form Template:**
- Class = blank registration form (template)
- Object = filled-out form (instance)
- Each filled form has the same structure, but different data

```python
# Class = Blueprint/Template
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

# Objects = Instances with actual data
person1 = Person("Godson", 25)    # One filled form
person2 = Person("Jarvis", 1)    # Another filled form
```

### Class Docstring `"""Holds all..."""`
- Describes what the class does
- Accessed via `help(Config)` or `Config.__doc__`

### `def __init__(self):`
- `def` = define a function (inside a class, it's called a **method**)
- `__init__` = special "initializer" method (constructor)
- The double underscores `__` mean it's a "magic method"
- Python calls `__init__` automatically when you create an object
- `self` = refers to the current object being created

### Why `self`?
```python
# When you write:
config = Config()

# Python does this behind the scenes:
Config.__init__(config)  # 'self' becomes 'config'
```

### `pass`
- A placeholder that does nothing
- Required because Python needs at least one line in a function
- We'll replace this with real code

---

## Step 4: Adding Project Root Path

```python
self.project_root = Path("/Volumes/samsungT5/my_projects/jarvis").absolute()
```

### Breaking Down This Line:

**`self.project_root`**
- `self` = the Config object we're creating
- `.project_root` = creating an **attribute** (a variable attached to the object)
- After this, we can access it: `config.project_root`

**`Path("/Volumes/samsungT5/my_projects/jarvis")`**
- Creates a `Path` object from the string
- This is our project's location on your Samsung T5 external drive

**`.absolute()`**
- Converts to an absolute (full) path
- Relative: `../jarvis` → Absolute: `/Volumes/samsungT5/my_projects/jarvis`
- Ensures we always have the complete path

### Deep Dive: What is `.absolute()`?

There are two types of file paths:

**Relative Path** (relative to where you are now):
```
./config.py          → "config.py in current folder"
../jarvis/config.py  → "go up one folder, then into jarvis"
models/whisper       → "models folder inside current folder"
```

**Absolute Path** (the FULL path from the root):
```
/Volumes/samsungT5/my_projects/jarvis/config.py
```

**What `.absolute()` does:**
```python
from pathlib import Path

# Imagine you're in: /Volumes/samsungT5/my_projects/
relative = Path("jarvis")
print(relative)            # jarvis

absolute = relative.absolute()
print(absolute)            # /Volumes/samsungT5/my_projects/jarvis
```

**In our code**, since we're already giving a full path starting with `/`, 
`.absolute()` isn't strictly necessary, but it's a good habit because:
1. It ensures the path is always absolute
2. It resolves any `..` or `.` in the path
3. It makes debugging easier - you always see the full path

### Why Use `self.`?

```python
class Config:
    def __init__(self):
        # WITH self - stored in object, accessible later:
        self.project_root = Path("/Volumes/...")
        
        # WITHOUT self - local variable, disappears after __init__:
        project_root = Path("/Volumes/...")

# With self:
config = Config()
print(config.project_root)  # ✅ Works!

# Without self:
config = Config()
print(config.project_root)  # ❌ Error! Attribute doesn't exist
```

---

## Step 5: Platform Detection

```python
self.is_mac = platform.system() == "Darwin"
self.is_windows = platform.system() == "Windows"
self.is_linux = platform.system() == "Linux"
```

### What's Happening Here:

**`platform.system()`**
- Returns a string identifying the OS:
  - `"Darwin"` = macOS (Darwin is the Mac kernel name)
  - `"Windows"` = Windows
  - `"Linux"` = Linux

**`== "Darwin"`**
- This is a **comparison** that returns `True` or `False`
- So `self.is_mac` will be `True` on Mac, `False` otherwise

### Why Do We Need This?

Different operating systems work differently:

| Feature | Mac | Windows |
|---------|-----|---------|
| File paths | `/Users/name/` | `C:\Users\name\` |
| Open app command | `open -a Spotify` | `start Spotify.exe` |
| Python command | `python3` | `python` |

### Usage Example:
```python
if CONFIG.is_mac:
    subprocess.run(["open", "-a", "Spotify"])
elif CONFIG.is_windows:
    subprocess.run(["start", "Spotify.exe"])
```

---

## Step 6: Model Paths

```python
self.models_dir = self.project_root / "models"
self.whisper_model = "mlx-community/whisper-large-v3-turbo"
self.llm_dir = self.models_dir / "mistral-7b"
self.tts_dir = self.models_dir / "cosyvoice2"
```

### The `/` Operator with Path Objects

**This is one of the coolest features of `pathlib`!**

When you use `/` between `Path` objects and strings, it joins them:

```python
path = Path("/Volumes/samsungT5")
path / "my_projects" / "jarvis"
# Result: Path('/Volumes/samsungT5/my_projects/jarvis')
```

This is much cleaner than the old way:
```python
# Old way (ugly and error-prone):
path = "/Volumes/samsungT5" + "/" + "my_projects" + "/" + "jarvis"
```

### Our Model Structure:

```
jarvis/
└── models/                      ← self.models_dir
    ├── mistral-7b/              ← self.llm_dir (Brain)
    ├── cosyvoice2/              ← self.tts_dir (Voice)
    └── mlx-cache/               ← Whisper downloads here
```

### Why Different Model Path Types?

**`self.whisper_model = "mlx-community/whisper-large-v3-turbo"`**
- This is a HuggingFace model ID (like a URL)
- MLX downloads it automatically from the internet
- Gets cached in `mlx-cache/`

**`self.llm_dir = self.models_dir / "mistral-7b"`**
- This is a local path on your drive
- We need to download and convert the model ourselves

---

## Step 7: Audio & Wake Word Settings

```python
self.audio_sample_rate = 16000  # 16 kHz
self.chunk_duration = 0.5       # seconds
self.wake_word = "jarvis"
```

### What is Sample Rate?

**Sample rate** = how many times per second we measure the audio signal.

Think of it like frames in a video:
- Video: 30 frames/second = smooth motion
- Audio: 16,000 samples/second = clear speech

| Sample Rate | Quality | Use Case |
|-------------|---------|----------|
| 8,000 Hz | Phone quality | Telephone calls |
| 16,000 Hz | Speech quality | Voice assistants ✓ |
| 44,100 Hz | CD quality | Music |
| 48,000 Hz | Professional | Studio recording |

**We use 16,000 Hz because:**
- Whisper (our STT model) is optimized for 16 kHz
- Human speech doesn't need higher rates
- Lower = less data = faster processing

### What is Chunk Duration?

```python
self.chunk_duration = 0.5  # seconds
```

We don't process audio continuously - we process it in "chunks":
- Every 0.5 seconds, we grab audio data
- Smaller chunks = more responsive (but more CPU work)
- Larger chunks = more accurate (but feels laggy)

**0.5 seconds is a good balance!**

### Wake Word

```python
self.wake_word = "jarvis"
```

Like "Hey Siri" or "OK Google" - the word that activates the assistant.

---

## Step 8: The validate_paths Method

```python
def validate_paths(self):
    """Check if required directories exist, create if needed."""
    print(f"📂 Project root: {self.project_root}")
    
    if not self.models_dir.exists():
        self.models_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {self.models_dir}")
    
    cache_dir = self.models_dir / "mlx-cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    os.environ["MLX_CACHE_DIR"] = str(cache_dir)
    
    return True
```

### New Concepts Here:

**`def validate_paths(self):`**
- This is a **method** (a function inside a class)
- `self` refers to the Config object
- Unlike `__init__`, this method isn't called automatically

**`self.models_dir.exists()`**
- Path objects have built-in methods!
- `.exists()` returns `True` if the folder/file exists

**`.mkdir(parents=True, exist_ok=True)`**
- Creates a directory (folder)
- `parents=True` = create parent folders if needed
- `exist_ok=True` = don't error if folder already exists

**`os.environ["MLX_CACHE_DIR"] = str(cache_dir)`**
- Sets an **environment variable**
- Environment variables are global settings your computer uses
- MLX reads this to know where to cache downloaded models

---

## Step 9: Creating the Global Instance

```python
CONFIG = Config()
CONFIG.validate_paths()

print("=" * 50)
print("✅ Jarvis Configuration Loaded!")
print(f"🖥️  Platform: {'Mac' if CONFIG.is_mac else ...}")
```

### Why Create a Global Instance?

```python
# WITHOUT global instance (bad):
# Every file has to create its own Config:
config1 = Config()  # in main.py
config2 = Config()  # in stt_engine.py - different object!

# WITH global instance (good):
# Every file shares the same Config:
from config import CONFIG  # Same object everywhere!
```

### What Happens on Import?

When you write `from config import CONFIG`, Python:
1. Runs the entire `config.py` file
2. Creates the `Config()` object
3. Calls `validate_paths()`
4. Prints the welcome message
5. Gives you access to `CONFIG`

### The f-string with Conditional

```python
print(f"🖥️  Platform: {'Mac' if CONFIG.is_mac else 'Windows'}")
```

This is a **ternary conditional** inside an f-string:
- If `CONFIG.is_mac` is `True` → prints "Mac"
- Otherwise → prints "Windows"

Same as:
```python
if CONFIG.is_mac:
    platform_name = "Mac"
else:
    platform_name = "Windows"
print(f"🖥️  Platform: {platform_name}")
```

---

## ✅ config.py Complete!

You've just built your first file! Let's test it.

### Key Takeaways from config.py:

| Concept | What It Means |
|---------|---------------|
| `class` | Blueprint for creating objects |
| `self.` | Attaches variables to the object |
| `__init__` | Runs automatically when you create an object |
| `Path` | Modern way to work with file paths |
| `/` with Path | Joins paths together (not division!) |
| `.absolute()` | Converts to full path from root |
| `.exists()` | Checks if file/folder exists |
| `.mkdir()` | Creates a directory |
| `os.environ` | Dictionary of environment variables |
| Global instance | One shared object for all files |

### String Operations Used:

```python
"=" * 50           # Repeat string 50 times
f"Hello {name}"    # f-string: insert variable into string
```

### Ternary Conditional:
```python
# These are equivalent:
result = 'Mac' if CONFIG.is_mac else 'Windows'

# is the same as:
if CONFIG.is_mac:
    result = 'Mac'
else:
    result = 'Windows'
```

---

# 📁 File: `action_executor.py`

*(Coming next...)*

---

# 📚 Python Concepts Reference

## Classes vs Objects
| Term | Definition | Example |
|------|------------|---------|
| Class | Blueprint/template | `class Dog:` |
| Object | Instance created from class | `my_dog = Dog()` |
| Method | Function inside a class | `def bark(self):` |
| Attribute | Variable inside a class | `self.name = "Rex"` |

## Special Methods (Magic Methods)
| Method | When It's Called |
|--------|------------------|
| `__init__` | When creating a new object |
| `__str__` | When using `print(object)` |
| `__repr__` | When debugging in console |

## Import Styles
```python
# Import entire module
import os
os.path.exists("file.txt")

# Import specific item
from pathlib import Path
Path("file.txt").exists()

# Import with alias
import numpy as np
np.array([1, 2, 3])
```
