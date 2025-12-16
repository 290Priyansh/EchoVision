"""
Configuration file for Blind Navigation Assistance System
All tunable parameters are defined here for easy adjustment
"""

# ============================================
# CAMERA SETTINGS
# ============================================
CAMERA_INDEX = 1 # Change if using different camera
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
CAMERA_ORIENTATION = "landscape"  # Fixed for this system

# ============================================
# INFERENCE SETTINGS
# ============================================
INFERENCE_WIDTH = 256  # Smaller for speed
INFERENCE_HEIGHT = 196
MODEL_NAME = "depth-anything/Depth-Anything-V2-Small-hf"
DEVICE = "cuda"  # "auto", "cuda", or "cpu"

# ============================================
# DEPTH ESTIMATION SETTINGS
# ============================================
# Depth threshold for "close" objects (0.0 = closest, 1.0 = farthest)
# Calibrate this value based on your environment
CLOSE_OBJECT_THRESHOLD = 0.20  # Objects closer than this trigger alerts

# Temporal smoothing to reduce flickering
SMOOTHING_FRAMES = 2

# ============================================
# REGION DIVISION SETTINGS
# ============================================
# Screen is divided into 3 vertical regions in landscape mode
NUM_REGIONS = 3
REGION_NAMES = ["LEFT", "CENTER", "RIGHT"]
# CENTER region is priority - if clear, path is safe
CENTER_CLEAR_THRESHOLD = 5.0  # If CENTER has < 5% occupancy, it's "clear"

# Side regions only alert if they have MAJOR presence
SIDE_ALERT_THRESHOLD = 10.0  # Side must have > 10% occupancy to alert

# Minimum object size (keep this)
MIN_OBJECT_PIXELS = 800

# Path clear if less than this % of frame is close objects
PATH_CLEAR_THRESHOLD = 0.5
# Minimum percentage of object pixels that must be in a region to trigger detection

# E.g., 15% means at least 15% of the object must occupy a region
MIN_OBJECT_OCCUPANCY_PERCENT = 10.0

# ============================================
# GUIDANCE SETTINGS
# ============================================
# Turn angle recommendations (in degrees)
PATH_CLEAR_THRESHOLD = 0.5
TURN_ANGLE_SMALL = 15   # For objects slightly off-center
TURN_ANGLE_MEDIUM = 30  # For objects moderately off-center
TURN_ANGLE_LARGE = 45   # For objects significantly off-center

# Distance categories (based on normalized depth)
DISTANCE_VERY_CLOSE = 0.15  # < 0.15
DISTANCE_CLOSE = 0.40       # 0.15 - 0.25
DISTANCE_MODERATE = 0.70    # 0.25 - 0.40
# > 0.40 is considered far

# Priority for multi-region detection
REGION_PRIORITY = ["CENTER", "LEFT", "RIGHT"]  # Check center first

# ============================================
# VISUALIZATION SETTINGS
# ============================================
# Colors for region overlays (BGR format)
COLOR_LEFT_REGION = (255, 0, 0)      # Blue
COLOR_CENTER_REGION = (0, 255, 0)    # Green
COLOR_RIGHT_REGION = (0, 0, 255)     # Red

# Alert overlay settings
ALERT_COLOR = (0, 0, 255)  # Red for close objects
ALERT_ALPHA = 0.5          # Transparency (0.0 - 1.0)

# Text display settings
FONT = 0  # cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.6
FONT_THICKNESS = 1
TEXT_COLOR = (0, 255, 0)  # Green

# ============================================
# GUI SETTINGS
# ============================================
GUI_WIDTH = 800
GUI_HEIGHT = 600
GUI_TITLE = "Blind Navigation Assistance System"
UPDATE_INTERVAL_MS = 30  # GUI update rate in milliseconds

# Button configurations
BUTTON_WIDTH = 20
BUTTON_HEIGHT = 2
BUTTON_FONT = ("Arial", 12, "bold")

# ============================================
# AUDIO FEEDBACK SETTINGS - Piper TTS
# ============================================
ENABLE_AUDIO = True  # Master audio switch
AUDIO_VOLUME = 0.8  # 0.0 to 1.0

# Piper TTS Model Configuration
import languages
DEFAULT_LANGUAGE = languages.LANG_ENGLISH
PIPER_MODELS_DIR = "./piper_models"  # Directory for voice models

# Current Language Settings (can be overridden at runtime)
CURRENT_LANGUAGE = DEFAULT_LANGUAGE
PIPER_MODEL_PATH = languages.MODEL_PATHS[DEFAULT_LANGUAGE]["model"]
PIPER_CONFIG_PATH = languages.MODEL_PATHS[DEFAULT_LANGUAGE]["config"]

# Speech timing control
SPEECH_COOLDOWN_MS = 300  # Fast response - 0.3 seconds
REPEAT_SAME_MESSAGE = False  # Repeat if same guidance multiple times

# Message priority settings
SPEAK_ON_STATUS_CHANGE = True  # Announce "Detection started", etc.
SPEAK_ON_CLEAR_PATH = False  # Announce "Path clear" (can be annoying)
SPEAK_CONTINUOUS = False  # If True, repeat guidance continuously

# ============================================
# DETECTION SENSITIVITY PRESETS
# ============================================
SENSITIVITY_PRESETS = {
    "low": {
        "threshold": 0.30,
        "min_occupancy": 25.0
    },
    "medium": {
        "threshold": 0.20,
        "min_occupancy": 15.0
    },
    "high": {
        "threshold": 0.15,
        "min_occupancy": 10.0
    }
}

DEFAULT_SENSITIVITY = "medium"

# ============================================
# LOGGING SETTINGS
# ============================================
ENABLE_LOGGING = True
LOG_FILE = "navigation_system.log"
LOG_LEVEL = "INFO"  # "DEBUG", "INFO", "WARNING", "ERROR"

# ============================================
# PERFORMANCE SETTINGS
# ============================================
TARGET_FPS = 30
ENABLE_FPS_DISPLAY = True
ENABLE_DEBUG_OVERLAY = True  # Show region boundaries and statistics

# ============================================
# FALSE POSITIVE FILTERING
# ============================================

# FILTER 1: Minimum object size (pixels)
# Filters out noise and distant small objects
MIN_OBJECT_PIXELS = 800  # Start here, adjust down if missing real objects
# 640x480 = 307,200 total pixels
# 800 = 0.26% of frame

# FILTER 2: Path clear threshold (% of frame with close objects)
# If less than this, path is considered clear
PATH_CLEAR_THRESHOLD = 0.5  # 0.5% of frame
# 0.5% = ~1,536 pixels at 640x480

# FILTER 3: Minimum depth variance (only if needed)
# If variance is too low, scene is uniform (empty)
MIN_DEPTH_VARIANCE = 120.0  # Add only if Steps 1&2 aren't enough
# Lower = more scenes pass (more sensitive)
# Higher = fewer scenes pass (less sensitive)