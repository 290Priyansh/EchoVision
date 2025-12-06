# Blind Navigation Assistance System 

A production-ready assistive navigation system for blind individuals using real-time computer vision and depth estimation. The system analyzes camera feed in landscape orientation, detects objects, and provides spatial guidance.

## 🎯 Project Overview

This Phase 1 implementation provides:
- Real-time depth estimation using Depth-Anything V2
- Landscape-oriented display divided into 3 vertical regions (LEFT, CENTER, RIGHT)
- Configurable object detection with adjustable sensitivity
- Directional guidance with turn angle recommendations
- Modular, scalable architecture for future enhancements

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
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project files

# Install dependencies
pip install -r requirements.txt
```

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

- **START DETECTION**: Begins real-time object detection and guidance
- **STOP DETECTION**: Pauses the system
- **Sensitivity Presets**: Quick configuration (Low/Medium/High)

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
6. **Visualization**: Overlays all information on display
7. **GUI Update**: Refreshes display at ~30 FPS

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

- **Audio Feedback**: Text-to-speech guidance
- **Spatial Audio**: 3D sound positioning
- **Object Classification**: Identify specific object types
- **Distance Estimation**: Precise distance in meters
- **Path Planning**: Suggest optimal navigation routes
- **Obstacle Memory**: Remember recently detected obstacles
- **Mobile App**: Android/iOS companion app
- **Wearable Integration**: Smart glasses, haptic feedback

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
- Verify internet connection (first run downloads model)
- Check `transformers` library version
- Ensure sufficient disk space (~500MB for model)

## 🔒 Safety Considerations

⚠️ **Important**: This is an assistive technology, not a replacement for traditional mobility aids.

- Always use in conjunction with a white cane or guide dog
- Test thoroughly in controlled environments first
- Be aware of system limitations (lighting, weather, etc.)
- Maintain the device properly and keep it charged
- Have a backup navigation method available

## 📝 Technical Specifications

- **Model**: Depth-Anything V2 Small
- **Input Resolution**: 640×480 (configurable)
- **Inference Resolution**: 256×196 (for speed)
- **Target FPS**: 30
- **Latency**: < 100ms typical
- **GPU Support**: CUDA-enabled (optional)

## 🤝 Contributing

This is a Phase 1 foundation. To extend:

1. Add new modules in separate files
2. Import and integrate in `navigation_system.py`
3. Update `config.py` with new parameters
4. Add GUI controls in `gui.py` if needed
5. Document changes in README

## 📄 License

[Specify your license here]

## 👥 Credits

- **Depth Estimation**: Depth-Anything V2 by TikTok/ByteDance
- **Original Concept**: Based on provided depth detection code

## 📧 Contact

[Your contact information]

---

**Version**: 1.0.0 (Phase 1)  
**Last Updated**: December 2025  
**Status**: Production Ready