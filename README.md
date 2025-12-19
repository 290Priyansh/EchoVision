# EchoVision- Real Time Edge Vision Assistant

A production-ready assistive navigation system for blind individuals using real-time computer vision, depth estimation, and **high-quality voice guidance**. The system analyzes camera feed in landscape orientation, detects objects, and provides spatial audio feedback using **Piper TTS**.

## 🎯 Project Overview

This implementation provides:
- Real-time depth estimation using Depth-Anything V2
- Landscape-oriented display divided into 3 vertical regions (LEFT, CENTER, RIGHT)
- **High-quality voice guidance using Piper TTS** (neural text-to-speech)
- Configurable object detection with adjustable sensitivity
- Directional guidance with turn angle recommendations
- Modular, scalable architecture for future enhancements

## ✨ Key Features

- 🎤 **Professional Voice Guidance**: Natural-sounding audio using Piper neural TTS
- 📹 **Real-time Object Detection**: 30 FPS depth estimation and spatial analysis
- 🎯 **Precise Directional Instructions**: "Object on left, move right by 45 degrees"
- ⚙️ **Adjustable Sensitivity**: Three presets plus fine-tuning controls
- 🔊 **Smart Audio Management**: Cooldown timers, message deduplication, priority alerts
- 🖥️ **User-Friendly GUI**: Tkinter interface with live video and controls

## 📁 Project Structure

```
blind-navigation-system/
├── main.py                    # Application entry point
├── config.py                  # Configuration settings
├── navigation_system.py       # Main system controller
├── video_capture.py           # Camera input handler
├── depth_estimation.py        # Depth analysis using AI model
├── region_analyzer.py         # Spatial region analysis
├── guidance_engine.py         # Direction guidance logic
├── visualizer.py              # Display overlay module
├── gui.py                     # Tkinter GUI interface
├── audio_feedback.py          # Piper TTS audio module (NEW)
├── requirements.txt           # Python dependencies
├── PIPER_SETUP.md            # Piper TTS installation guide (NEW)
├── README.md                  # This file
└── piper_models/              # Voice model files (NEW)
    ├── en_US-lessac-medium.onnx
    └── en_US-lessac-medium.onnx.json
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project files

# Install dependencies
pip install -r requirements.txt

# Download Piper voice model (see PIPER_SETUP.md for details)
mkdir piper_models
cd piper_models
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-lessac-medium.onnx
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-lessac-medium.onnx.json
cd ..
```

**Important**: See **PIPER_SETUP.md** for complete audio setup instructions.

### 2. Configuration

Edit `config.py` to customize:
- Camera settings (index, resolution)
- Detection thresholds
- Turn angle recommendations
- Region occupancy percentages
- Visual display options

### 3. Run the System

```bash
python main.py
```

## 🎮 Using the GUI

### Main Controls

- **START DETECTION**: Begins real-time object detection and voice guidance
- **STOP DETECTION**: Pauses the system
- **Sensitivity Presets**: Quick configuration (Low/Medium/High)
- **Test Audio**: Verify voice output is working

### Audio Controls (NEW)

- **Enable Voice Guidance**: Toggle audio on/off
- **Test Audio**: Play sample message to verify audio works

### Adjustable Settings

- **Detection Threshold** (0.05 - 0.50): Distance at which objects trigger alerts
  - Lower values = more sensitive to distant objects
  - Higher values = only detect very close objects
  
- **Min Occupancy %** (5% - 50%): Minimum object presence required in a region
  - Lower values = detect smaller objects
  - Higher values = only trigger on larger objects

### Display Options

- **Show Regions**: Display vertical region boundaries
- **Show Statistics**: Show detection stats in top-right corner
- **Show Depth Map**: Toggle between camera view and depth visualization

## 🔧 Configuration Details

### Region Division

The screen is divided into **3 equal vertical regions**:
- **LEFT**: Objects on the left side
- **CENTER**: Objects directly ahead
- **RIGHT**: Objects on the right side

### Turn Angle Recommendations

Configured in `config.py`:
- **TURN_ANGLE_SMALL** = 15° (slight adjustments)
- **TURN_ANGLE_MEDIUM** = 30° (moderate turns)
- **TURN_ANGLE_LARGE** = 45° (significant direction changes)

### Distance Categories

- **Very Close**: < 0.15 (normalized depth)
- **Close**: 0.15 - 0.25
- **Moderate**: 0.25 - 0.40
- **Far**: > 0.40

### Sensitivity Presets

**Low Sensitivity:**
- Threshold: 0.30 (only very close objects)
- Min Occupancy: 25% (large objects only)

**Medium Sensitivity (Default):**
- Threshold: 0.20 (moderate distance)
- Min Occupancy: 15% (balanced detection)

**High Sensitivity:**
- Threshold: 0.15 (detects further objects)
- Min Occupancy: 10% (small objects detected)

## 📊 Guidance Message Format

The system generates messages in this format:

```
Object detected in [REGION], move [DIRECTION] by [ANGLE] degrees
```

**Examples:**
- "Object detected on left, move right by 45 degrees"
- "Object ahead and slightly left, move right by 15 degrees"
- "Object detected on right side, move left by 30 degrees"
- "Path clear"

## 🎨 Visual Indicators

### Color Coding

- **Red Overlay**: Objects closer than threshold
- **Green Text**: Normal status, good FPS
- **Yellow/Orange Text**: Medium urgency
- **Red Text**: High urgency, critical proximity

### On-Screen Information

- **Status**: System active/paused
- **FPS**: Current frame rate
- **Threshold**: Current detection threshold
- **Occupancy Bars**: Shows % of object in each region
- **Detection Statistics**: Detailed region analysis
- **Guidance Message**: Current directional instruction

## 🔍 How It Works

### Processing Pipeline

1. **Video Capture**: Captures frame from camera in landscape mode
2. **Depth Estimation**: AI model predicts depth map (0.0 = close, 1.0 = far)
3. **Object Masking**: Identifies objects closer than threshold
4. **Region Analysis**: Calculates object distribution across 3 regions
5. **Guidance Generation**: Determines direction and turn angle
6. **Audio Output**: Speaks guidance using Piper TTS (NEW)
7. **Visualization**: Overlays all information on display
8. **GUI Update**: Refreshes display at ~30 FPS

### Key Algorithms

**Region Occupancy Calculation:**
```
occupancy_percent = (object_pixels_in_region / total_object_pixels) × 100
```

**Primary Region Selection:**
- Region with highest occupancy percentage
- Must exceed MIN_OBJECT_OCCUPANCY_PERCENT threshold

**Turn Angle Determination:**
- Based on which regions contain objects
- Scaled by how much object spans multiple regions

## 🛠️ Calibration Guide

### Depth Threshold Calibration

1. Place a reference object at 1 meter distance
2. Run the system and observe the red overlay
3. Adjust the threshold slider until the object is just barely highlighted
4. This threshold value represents "1 meter" in your environment

### Occupancy Tuning

- **Crowded Environments**: Increase to 20-25% to avoid excessive alerts
- **Open Spaces**: Decrease to 10-15% to detect smaller obstacles
- **Testing**: Use different sized objects and adjust until detection feels natural

## 📈 Future Enhancements (Phase 2+)

### Planned Features

- **Spatial Audio**: 3D sound positioning (object sounds come from its direction)
- **Haptic Feedback**: Vibration patterns for wearables
- **Object Classification**: Identify specific object types (person, car, chair)
- **Distance Estimation**: Precise distance in meters/feet
- **Path Planning**: Suggest optimal navigation routes
- **Obstacle Memory**: Remember recently detected obstacles
- **Mobile App**: Android/iOS companion app
- **Wearable Integration**: Smart glasses support
- **Multiple Languages**: Voice guidance in 40+ languages
- **Offline Maps**: Pre-loaded navigation for indoor spaces

## 🐛 Troubleshooting

### Camera Not Found
- Check `CAMERA_INDEX` in `config.py`
- Try different values (0, 1, 2, etc.)
- Verify camera permissions

### Low FPS
- Reduce `INFERENCE_WIDTH` and `INFERENCE_HEIGHT` in `config.py`
- Use GPU if available (automatically detected)
- Close other applications using the camera

### False Detections
- Increase `MIN_OBJECT_OCCUPANCY_PERCENT`
- Adjust `CLOSE_OBJECT_THRESHOLD` to be more conservative
- Ensure proper lighting in the environment

### Model Loading Issues
- Verify internet connection (first run downloads Depth-Anything model)
- Check `transformers` library version
- Ensure sufficient disk space (~500MB for depth model, ~30MB for voice model)

### Audio Not Working
- Check **PIPER_SETUP.md** for complete installation guide
- Verify voice model files exist in `piper_models/` directory
- Test system audio with other applications
- Click "Test Audio" button in GUI
- Check `ENABLE_AUDIO = True` in config.py
- Ensure PyAudio is installed: `pip install pyaudio`

## 🔒 Safety Considerations

⚠️ **Important**: This is an assistive technology, not a replacement for traditional mobility aids.

- Always use in conjunction with a white cane or guide dog
- Test thoroughly in controlled environments first
- Be aware of system limitations (lighting, weather, etc.)
- Maintain the device properly and keep it charged
- Have a backup navigation method available

## 📝 Technical Specifications

- **Depth Model**: Depth-Anything V2 Small
- **Audio Engine**: Piper TTS (neural text-to-speech)
- **Voice Model**: en_US-lessac-medium (female, clear)
- **Input Resolution**: 640×480 (configurable)
- **Inference Resolution**: 256×196 (for speed)
- **Target FPS**: 30
- **Audio Latency**: 50-150ms
- **Total Latency**: < 200ms typical
- **GPU Support**: CUDA-enabled (optional)

## 🤝 Contributing

This is a Phase 1 foundation. To extend:

1. Add new modules in separate files
2. Import and integrate in `navigation_system.py`
3. Update `config.py` with new parameters
4. Add GUI controls in `gui.py` if needed
5. Document changes in README
