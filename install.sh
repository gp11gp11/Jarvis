#!/bin/bash
# install.sh - Jarvis AI Installation Script for /Volumes/samsungT5/my_projects/jarvis

set -e  # Exit on error

PROJECT_ROOT="/Volumes/samsungT5/my_projects/jarvis"

echo "🚀 Jarvis AI Installation Script"
echo "📍 Installing to: $PROJECT_ROOT"

# Check if project directory exists
if [ ! -d "$PROJECT_ROOT" ]; then
    echo "❌ Project directory not found at $PROJECT_ROOT"
    echo "💡 Please check your external drive is mounted and the path is correct"
    exit 1
fi

# Navigate to project directory
cd "$PROJECT_ROOT"

# Create directory structure
echo "🏗️ Creating directory structure..."
mkdir -p models/mlx-whisper
mkdir -p models/mistral-7b
mkdir -p models/cosyvoice2
mkdir -p src
mkdir -p data
mkdir -p scripts

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install numpy librosa sounddevice pyaudio requests python-dotenv tqdm

# Install MLX
echo "⚡ Installing MLX framework..."
pip install mlx mlx-whisper mlx-lm

# Install CosyVoice2 dependencies
echo "🗣️ Setting up CosyVoice2..."
pip install torch torchaudio  # Required for CosyVoice2
pip install soundfile pydub

# Clone CosyVoice2 repository
echo "📥 Cloning CosyVoice2 repository..."
if [ ! -d "models/cosyvoice2" ]; then
    git clone https://github.com/FunAudioLLM/CosyVoice2-0.5B.git models/cosyvoice2
else
    echo "✅ CosyVoice2 repository already exists"
fi

# Create requirements file
cat > requirements.txt << EOF
numpy==1.26.0
librosa==0.10.1
sounddevice==0.4.6
pyaudio==0.2.13
requests==2.31.0
python-dotenv==1.0.0
mlx==0.0.10
mlx-whisper==0.0.5
mlx-lm==0.0.8
torch==2.1.0
torchaudio==2.1.0
soundfile==0.12.1
pydub==0.25.1
tqdm==4.66.1
EOF

# Set project root explicitly
PROJECT_ROOT="/Volumes/samsungT5/my_projects/jarvis"

# Create cache directories with proper permissions
mkdir -p "$PROJECT_ROOT/models/hf-cache"
mkdir -p "$PROJECT_ROOT/models/hf-cache/hub"
mkdir -p "$PROJECT_ROOT/models/mlx-cache"
mkdir -p "$PROJECT_ROOT/models/mlx-whisper"

# Set permissions explicitly (this is crucial for external drives)
chmod -R 755 "$PROJECT_ROOT/models"
chown -R $(whoami) "$PROJECT_ROOT/models" 2>/dev/null || true

# Set ALL Hugging Face cache variables
export HF_HOME="$PROJECT_ROOT/models/hf-cache"
export HF_HUB_CACHE="$HF_HOME/hub"
export HUGGINGFACE_HUB_CACHE="$HF_HOME/hub"
export TRANSFORMERS_CACHE="$PROJECT_ROOT/models/hf-cache/transformers"
export DATASETS_CACHE="$PROJECT_ROOT/models/hf-cache/datasets"
export MLX_CACHE_DIR="$PROJECT_ROOT/models/mlx-cache"

# Verify the variables are set
echo "HF_HOME: $HF_HOME"
echo "HF_HUB_CACHE: $HF_HUB_CACHE"
echo "MLX_CACHE_DIR: $MLX_CACHE_DIR"

# Create startup script
cat > start_jarvis.sh << EOF
#!/bin/bash
# start_jarvis.sh - Start Jarvis AI from external drive

# Navigate to project directory
cd "\$(dirname "\$0")"


# Set MLX cache directory
export MLX_CACHE_DIR="\$(pwd)/models/mlx-cache"

# Set Python path
export PYTHONPATH="\$(pwd)/src:\$(pwd)/models/cosyvoice2:\$PYTHONPATH"

# Start Jarvis
python src/main.py
EOF

chmod +x start_jarvis.sh

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "🚀 Next Steps:"
echo "1. Download the models (run the model download commands below)"
echo "2. Copy the source code files to src/ directory"
echo "3. Run ./start_jarvis.sh to start Jarvis"
echo ""
echo "📥 Model Download Commands:"
echo ""
echo "# For Whisper model:"
echo "HF_HOME=\"$HF_HOME\" HF_HUB_CACHE=\"$HF_HUB_CACHE\" HUGGINGFACE_HUB_CACHE=\"$HUGGINGFACE_HUB_CACHE\" TRANSFORMERS_CACHE=\"$TRANSFORMERS_CACHE\" DATASETS_CACHE=\"$DATASETS_CACHE\" MLX_CACHE_DIR=\"$MLX_CACHE_DIR\" python -c \"import mlx_whisper; print('Downloading Whisper model...'); mlx_whisper.transcribe('test.wav', model='mlx-community/whisper-large-v3-turbo', download_root='$PROJECT_ROOT/models/mlx-whisper')\""
echo ""
echo "# For Mistral-7B model:"
echo "python -c \"from mlx_lm import convert; print('Converting Mistral-7B model...'); convert.convert('mistralai/Mistral-7B-Instruct-v0.2', '$PROJECT_ROOT/models/mistral-7b', quantize=True, q_group_size=64, q_bits=4)\""
echo ""
echo "# For CosyVoice2 model:"
echo "cd $PROJECT_ROOT/models/cosyvoice2"
echo "python download_model.py --model cosyvoice2-0.5b --output_dir $PROJECT_ROOT/models/cosyvoice2/models"
echo "cd $PROJECT_ROOT"
echo ""
echo "💡 Important Notes:"
echo "   • Keep your Samsung T5 drive connected during operation"
echo "   • First run will take longer as models load into memory"
echo "   • For best performance, use USB-C connection"
echo ""
echo "🔧 To test the installation:"
echo "./start_jarvis.sh"