# Piper TTS Setup Guide

Complete instructions for installing and configuring Piper TTS for the Blind Navigation System.

## 📦 Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `piper-tts` - The Piper TTS library
- `pyaudio` - Audio playback
- All other project dependencies

---

## 🎤 Step 2: Download Voice Models

Piper requires voice model files to work. You need to download them separately.

### Option A: Automatic Download (Recommended)

```bash
# Create models directory
mkdir piper_models
cd piper_models

# Download recommended voice (female, clear, ~30MB)
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-lessac-medium.onnx
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-lessac-medium.onnx.json

# Return to project root
cd ..
```

### Option B: Manual Download

1. Go to: https://github.com/rhasspy/piper/releases/tag/v1.2.0
2. Download these files:
   - `en_US-lessac-medium.onnx` (Voice model file)
   - `en_US-lessac-medium.onnx.json` (Configuration file)
3. Place both files in `piper_models/` directory

---

## 🗂️ Project Structure

After setup, your project should look like this:

```
blind-navigation-system/
├── main.py
├── config.py
├── navigation_system.py
├── video_capture.py
├── depth_estimation.py
├── region_analyzer.py
├── guidance_engine.py
├── visualizer.py
├── gui.py
├── audio_feedback.py          ← New audio module
├── requirements.txt
├── PIPER_SETUP.md
├── README.md
└── piper_models/               ← Voice models directory
    ├── en_US-lessac-medium.onnx
    └── en_US-lessac-medium.onnx.json
```

---

## 🎭 Available Voice Options

### English (US) Voices

| Voice | Gender | Quality | Size | Speed |
|-------|--------|---------|------|-------|
| **en_US-lessac-medium** ⭐ | Female | Clear | 30MB | Fast |
| en_US-ryan-medium | Male | Warm | 30MB | Fast |
| en_US-libritts-high | Both | Best | 50MB | Medium |
| en_US-amy-medium | Female | Natural | 30MB | Fast |

### English (UK) Voices

| Voice | Gender | Quality | Size |
|-------|--------|---------|------|
| en_GB-alan-medium | Male | British | 30MB |
| en_GB-jenny_dioco-medium | Female | British | 30MB |

### Other Languages

Piper supports 40+ languages including:
- Spanish: `es_ES-*`
- French: `fr_FR-*`
- German: `de_DE-*`
- Italian: `it_IT-*`

Full list: https://rhasspy.github.io/piper-samples/

---

## 🔧 Configuration

Edit `config.py` to change voice settings:

```python
# Piper TTS Model Configuration
PIPER_MODELS_DIR = "./piper_models"
PIPER_MODEL_PATH = "./piper_models/en_US-lessac-medium.onnx"
PIPER_CONFIG_PATH = "./piper_models/en_US-lessac-medium.onnx.json"

# Audio settings
ENABLE_AUDIO = True
AUDIO_VOLUME = 0.8
SPEECH_COOLDOWN_MS = 2000  # 2 seconds between messages
```

---

## 🚀 Quick Test

Test if Piper is working correctly:

```python
from piper import PiperVoice

# Load voice
voice = PiperVoice.load("piper_models/en_US-lessac-medium.onnx")

# Synthesize test
import wave
wav_file = wave.open("test.wav", "wb")
wav_file.setnchannels(1)
wav_file.setsampwidth(2)
wav_file.setframerate(voice.config.sample_rate)
voice.synthesize("Hello, this is a test of Piper text to speech", wav_file)
wav_file.close()

print("✅ Test successful! Check test.wav")
```

---

## 🐛 Troubleshooting

### Error: "FileNotFoundError: Model file not found"

**Solution**: Check that model files exist:
```bash
ls -la piper_models/
# Should show .onnx and .onnx.json files
```

### Error: "ImportError: No module named 'piper'"

**Solution**: Install piper-tts:
```bash
pip install piper-tts
```

### Error: "PyAudio not found" (Linux)

**Solution**: Install system dependencies first:
```bash
# Ubuntu/Debian
sudo apt-get install portaudio19-dev python3-pyaudio

# Then install PyAudio
pip install pyaudio
```

### Error: "PyAudio not found" (Mac)

**Solution**:
```bash
brew install portaudio
pip install pyaudio
```

### Error: "PyAudio not found" (Windows)

**Solution**: Download pre-built wheel:
```bash
# Go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# Download appropriate .whl file for your Python version
pip install PyAudio‑0.2.13‑cp311‑cp311‑win_amd64.whl
```

### No audio output

**Checklist**:
1. ✅ System volume not muted
2. ✅ `ENABLE_AUDIO = True` in config.py
3. ✅ Audio checkbox enabled in GUI
4. ✅ Model files exist in correct location
5. ✅ Click "Test Audio" button in GUI

---

## 🎯 Performance Tips

### For Faster Speech:
```python
# Use "low" quality models (smaller, faster)
PIPER_MODEL_PATH = "./piper_models/en_US-lessac-low.onnx"
```

### For Better Quality:
```python
# Use "high" quality models (larger, slower)
PIPER_MODEL_PATH = "./piper_models/en_US-libritts-high.onnx"
```

### For Raspberry Pi:
- Use "low" quality models
- Reduce `SPEECH_COOLDOWN_MS` if needed
- Consider using smaller inference size for depth estimation

---

## 📊 Model Comparison

| Model Quality | Synthesis Speed | Audio Quality | File Size |
|---------------|-----------------|---------------|-----------|
| Low | 0.05s | Good | ~10MB |
| **Medium** ⭐ | 0.10s | Excellent | ~30MB |
| High | 0.20s | Best | ~50MB |

**Recommendation**: Use **Medium** for best balance of speed and quality.

---

## 🔊 Audio System Architecture

```
┌─────────────────────────────────────────┐
│  Navigation System                       │
│  └─ process_frame()                     │
│     └─ generate_guidance()              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  AudioFeedback (audio_feedback.py)      │
│  ├─ speak_guidance()                    │
│  └─ speech_queue (thread-safe)          │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Piper TTS Engine                       │
│  └─ voice.synthesize(text)              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  PyAudio Player                         │
│  └─ stream.write(audio_data)            │
└─────────────────────────────────────────┘
                 │
                 ▼
              🔊 Speaker
```

---

## ⚙️ Advanced Configuration

### Custom Voice Selection

Download additional voices and switch in config:

```python
# Male voice
PIPER_MODEL_PATH = "./piper_models/en_US-ryan-medium.onnx"

# British accent
PIPER_MODEL_PATH = "./piper_models/en_GB-alan-medium.onnx"

# Spanish
PIPER_MODEL_PATH = "./piper_models/es_ES-sharvard-medium.onnx"
```

### Adjust Speech Timing

```python
# More frequent guidance (shorter cooldown)
SPEECH_COOLDOWN_MS = 1000  # 1 second

# Less frequent (reduce audio fatigue)
SPEECH_COOLDOWN_MS = 3000  # 3 seconds

# Allow message repetition
REPEAT_SAME_MESSAGE = True
```

### Priority Messages

In `audio_feedback.py`, priority messages skip cooldown:

```python
# Normal message (respects cooldown)
audio.speak("Object on left")

# Priority message (immediate)
audio.speak("Warning! Very close object!", priority=True)
```

---

## 📝 Usage in Code

### Basic Usage:

```python
from audio_feedback import AudioFeedback

# Initialize
audio = AudioFeedback()
audio.initialize()

# Speak simple message
audio.speak("Navigation started")

# Speak with priority
audio.speak("Warning! Obstacle ahead", priority=True)

# Cleanup
audio.shutdown()
```

### With Guidance Engine:

```python
# Get guidance from system
guidance = guidance_engine.generate_guidance(analysis)

# Speak it
audio.speak_guidance(guidance)
# Automatically adds "Warning!" or "Caution" based on urgency
```

---

## 🎓 Learning Resources

- **Piper Documentation**: https://github.com/rhasspy/piper
- **Voice Samples**: https://rhasspy.github.io/piper-samples/
- **Model Downloads**: https://github.com/rhasspy/piper/releases
- **PyAudio Docs**: https://people.csail.mit.edu/hubert/pyaudio/

---

## ✅ Verification Checklist

Before running the full system:

- [ ] `pip install -r requirements.txt` completed
- [ ] `piper_models/` directory exists
- [ ] `.onnx` and `.onnx.json` files downloaded
- [ ] `config.py` updated with correct paths
- [ ] `ENABLE_AUDIO = True` in config
- [ ] PyAudio installed (test: `python -c "import pyaudio"`)
- [ ] System audio working
- [ ] Test audio button works in GUI

---

## 🚀 Ready to Run

Once everything is set up:

```bash
python main.py
```

Click **"Test Audio"** button to verify voice output works, then click **"START DETECTION"** to begin navigation with voice guidance!

---

**Questions?** Check the troubleshooting section or the main README.md for more help.