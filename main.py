import cv2
import torch
import numpy as np
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForDepthEstimation
import time
import warnings

warnings.filterwarnings('ignore')

# ============================================
# PHASE 1: SETUP & MODEL LOADING
# ============================================

print("Loading Depth-Anything V2 model...")
processor = AutoImageProcessor.from_pretrained(
    "depth-anything/Depth-Anything-V2-Small-hf",
    use_fast=True
)
model = AutoModelForDepthEstimation.from_pretrained(
    "depth-anything/Depth-Anything-V2-Small-hf"
)

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
model.eval()
print(f"✅ Model loaded on {device}")

# ============================================
# Configuration
# ============================================
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
INFERENCE_WIDTH = 256  # Smaller for speed
INFERENCE_HEIGHT = 196

# --- CALIBRATION ZONE ---
# 0.0 = The camera lens itself (closest possible)
# 1.0 = Infinity (farthest possible)
# Adjust this value to match "1 meter" in your specific room.
ONE_METER_THRESHOLD = 0.20
# ------------------------

SMOOTHING_FRAMES = 2
depth_history = []


# ============================================
# Helper Functions
# ============================================

def normalize_depth(depth_map):
    """
    Normalize depth map to 0-1 range.
    LOGIC: 0.0 = Closest, 1.0 = Farthest
    """
    depth_min = depth_map.min()
    depth_max = depth_map.max()

    if depth_max - depth_min > 0:
        # Standard normalization
        normalized = (depth_map - depth_min) / (depth_max - depth_min)

        # Depth Anything outputs 'disparity' (high value = close).
        # So (val - min)/(max - min) makes Close=1, Far=0.
        # We want Close=0 for your existing logic, so we invert it:
        normalized = 1.0 - normalized
    else:
        normalized = np.zeros_like(depth_map)

    return normalized


def apply_temporal_smoothing(depth_map):
    """Smooth depth over time to reduce flickering"""
    global depth_history
    depth_history.append(depth_map)
    if len(depth_history) > SMOOTHING_FRAMES:
        depth_history.pop(0)
    return np.mean(depth_history, axis=0)


def create_red_alert_overlay(frame, depth_map, threshold):
    """
    Creates a red overlay only where objects are closer than the threshold.
    """
    h, w = frame.shape[:2]

    # Create a mask where depth is LESS than threshold (meaning closer)
    # (Since we normalized so 0.0 is closest)
    mask = depth_map < threshold

    # Resize mask to match the actual frame size
    # depth_map is usually smaller due to inference size or previous resizing
    # ensuring it matches frame size exactly
    mask_resized = cv2.resize(mask.astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST)

    # Create a red layer
    # BGR Format: (0, 0, 255) is Red
    red_layer = np.zeros_like(frame)
    red_layer[:] = (0, 0, 255)

    # Blend the red layer onto the frame only where the mask is True
    # We use weighted add for transparency

    # 1. Create a copy of the frame to draw on
    overlay = frame.copy()

    # 2. Identify pixels to color
    # We want to blend red with the original pixels
    alpha = 0.5  # Transparency of the red

    # Extract the region of interest (ROI) where mask is active
    roi = overlay[mask_resized == 1]

    if roi.size > 0:
        # Blend the ROI with the red color
        # red_layer[mask_resized == 1] gives us the red pixels for that area
        blended_roi = cv2.addWeighted(roi, 1 - alpha, red_layer[mask_resized == 1], alpha, 0)

        # Put back into the image
        overlay[mask_resized == 1] = blended_roi

    return overlay


def draw_info(frame, fps, threshold):
    """Draws simple status text"""
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Threshold: {threshold}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(frame, "RED = < 1m (Approx)", (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    return frame


# ============================================
# Main Execution
# ============================================

# Camera Setup
cap = cv2.VideoCapture(1)  # Change index if needed
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

print("\n" + "=" * 50)
print("  DEPTH WARNING SYSTEM")
print("  Objects closer than threshold will turn RED")
print("  Press 'ESC' to quit")
print("=" * 50 + "\n")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        start_time = time.time()

        # 1. Preprocessing
        frame_small = cv2.resize(frame, (INFERENCE_WIDTH, INFERENCE_HEIGHT))
        pil_image = Image.fromarray(cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB))

        # 2. Inference
        inputs = processor(images=pil_image, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
            depth_map = outputs.predicted_depth.squeeze().cpu().numpy()

        # 3. Post-processing (Normalize)
        # Normalize so 0.0 is close, 1.0 is far
        depth_norm = normalize_depth(depth_map)
        depth_smooth = apply_temporal_smoothing(depth_norm)

        # Resize depth to match screen for the mask creation
        depth_resized = cv2.resize(depth_smooth, (frame.shape[1], frame.shape[0]))

        # 4. Visualization (Red Overlay)
        final_frame = create_red_alert_overlay(frame, depth_resized, ONE_METER_THRESHOLD)

        # 5. Info Display
        fps = 1.0 / (time.time() - start_time)
        final_frame = draw_info(final_frame, fps, ONE_METER_THRESHOLD)

        cv2.imshow("Depth Alert System", final_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break

except KeyboardInterrupt:
    print("Stopping...")
finally:
    cap.release()
    cv2.destroyAllWindows()
    print("System stopped.")