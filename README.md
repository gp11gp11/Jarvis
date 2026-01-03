# Jarvis AI Assistant

A fully local, offline AI voice assistant designed to run on Apple Silicon (M1/M2/M3) using MLX. This project is optimized to run entirely from an external Samsung T5 drive.

## 🚀 Overview

Jarvis listens for a wake word, transcribes your speech, understands your intent using a Large Language Model (LLM), executes system actions, and responds back to you with natural-sounding speech—all running locally on your Mac.

### Key Features
- **100% Local Privacy**: No data leaves your machine.
- **Apple Silicon Optimized**: Uses `mlx` for high-performance inference on M-series chips.
- **External Drive Ready**: Designed to store large models and run directly from external storage.
- **Voice Activated**: Continuously listens for the wake word "Jarvis".
- **Action Execution**: Can control system apps (Spotify, Apple Music) and answer queries.

---

## 🧠 Model Architecture

The system uses three specialized AI models:

| Component | Function | Model Used | Library |
|-----------|----------|------------|---------|
| **The Ear** (STT) | Transcribes speech to text | **Whisper Large v3 Turbo** (`mlx-community/whisper-large-v3-turbo`) | `mlx-whisper` |
| **The Brain** (LLM) | UNDERSTANDS & Generates text | **Mistral 7B Instruct v0.2** (4-bit Quantized) | `mlx-lm` |
| **The Mouth** (TTS) | SYNTHESIZES text to speech | **CosyVoice2 0.5B** | `CosyVoice` / `torch` |

---

## 🛠️ System Requirements

- **Hardware**: Mac with Apple Silicon (M1/M2/M3)
- **RAM**: Minimum 16GB (64GB recommended for best performance)
- **Storage**: ~20GB of free space (External T5 drive recommended)
- **OS**: macOS Sonoma or later
- **Python**: 3.10+

---

## 📦 Installation

### 1. Prerequisite Setup
Ensure your external drive is mounted at `/Volumes/samsungT5`.

### 2. Auto-Install
Run the included installation script to set up directories and install dependencies:

```bash
./install.sh
```

### 3. Model Download
The models are large and need to be downloaded explicitly. Run the commands output by the install script:

**Download Whisper (STT)**:
```bash
# This happens automatically on first run, but you can force it:
python -c "import mlx_whisper; mlx_whisper.transcribe('test.wav', path_or_hf_repo='mlx-community/whisper-large-v3-turbo')"
```

**Download Mistral (LLM)**:
```bash
# Convert and quantize the model
python -c "from mlx_lm import convert; convert.convert('mistralai/Mistral-7B-Instruct-v0.2', '/Volumes/samsungT5/my_projects/jarvis/models/mistral-7b', quantize=True, q_group_size=64, q_bits=4)"
```

**Download CosyVoice2 (TTS)**:
```bash
cd models/cosyvoice2
# Follow CosyVoice2 official instructions to download the 0.5B model checkpoint
```

---

## 🕹️ Usage

### Starting Jarvis
To start the assistant, run the startup script:

```bash
./start_jarvis.sh
```

### Interactions
1.  **Wake Up**: Say "Jarvis" to get its attention.
2.  **Commands**:
    *   "What time is it?"
    *   "Play some music on Spotify"
    *   "Open Apple Music"
    *   "Tell me a joke"
3.  **Shutdown**: Say "Exit", "Shutdown", or "Goodbye".

---

## 📂 Project Structure

```
jarvis/
├── start_jarvis.sh       # Main startup script
├── install.sh            # One-time installation script
├── requirements.txt      # Python dependencies
├── src/                  # Source code
│   ├── main.py           # Core event loop
│   ├── config.py         # Configuration settings
│   ├── stt_engine.py     # Speech-to-Text (Whisper)
│   ├── llm_engine.py     # LLM (Mistral)
│   ├── tts_engine.py     # Text-to-Speech (CosyVoice)
│   └── action_executor.py # System command handler
└── models/               # Model weights (Large files)
    ├── mlx-whisper/
    ├── mistral-7b/
    └── cosyvoice2/
```

## 🔧 Troubleshooting

- **Audio Permission Error**: Ensure your terminal (iTerm/Terminal) has permission to access the Microphone in System Settings > Privacy & Security > Microphone.
- **Model Load Error**: Check if the external drive is mounted. The path `/Volumes/samsungT5` must exist.
- **Slow Performance**: Close other heavy applications. LLMs and TTS Models are very RAM intensive.

## 🤝 Customization

To add new commands, edit `src/action_executor.py` and `src/llm_engine.py`.
1.  Add the intent in `llm_engine.py`'s `parse_action` method.
2.  Implement the logic in `action_executor.py`'s `execute_action` method.
