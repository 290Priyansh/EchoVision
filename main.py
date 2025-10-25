import cv2
import torch
import numpy as np
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForDepthEstimation
import time
import os
import json

# ----------------------------
# Load model + processor
# ----------------------------
processor = AutoImageProcessor.from_pretrained(
    "depth-anything/Depth-Anything-V2-Small-hf",
    use_fast=True
)
model = AutoModelForDepthEstimation.from_pretrained("depth-anything/Depth-Anything-V2-Small-hf")

# ----------------------------
# Device setup
# ----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
model.eval()
print(f"Using device: {device}")
if device == "cuda":
    print(f"GPU: {torch.cuda.get_device_name(torch.cuda.current_device())}")

# ----------------------------
# Camera setup
# ----------------------------
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("❌ Could not open camera")
    exit()

# ----------------------------
# Load or perform calibration
# ----------------------------
calibration_file = "calibration.json"

if os.path.exists(calibration_file):
    with open(calibration_file, "r") as f:
        calibration_data = json.load(f)
    a = calibration_data["a"]
    b = calibration_data["b"]
    print(f"✅ Loaded calibration: real_distance = {a:.4f}*depth + {b:.4f}")
else:
    print("Calibration step: place objects at known distances and press 'c' to record depth.")
    calibration_depths = []
    calibration_distances = []
    N_CALIBRATION_POINTS = int(input("Enter number of calibration points (e.g., 2 or 3): "))

    for i in range(N_CALIBRATION_POINTS):
        input(f"Place object at distance {i + 1} and press Enter...")
        print("Press 'c' while object is in center to record depth")
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            frame_small = cv2.resize(frame, (320, 240))
            cv2.imshow("Calibration", frame_small)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('c'):
                # Capture depth at center
                frame_rgb = cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame_rgb)
                inputs = processor(images=image, return_tensors="pt")
                inputs = {k: v.to(device) for k, v in inputs.items()}
                with torch.no_grad():
                    depth = model(**inputs).predicted_depth.squeeze().cpu().numpy()
                h, w = depth.shape
                center_depth = depth[h // 2, w // 2]
                calibration_depths.append(center_depth)
                real_distance = float(input(f"Enter actual distance in meters for this point: "))
                calibration_distances.append(real_distance)
                print(f"Recorded: model depth={center_depth:.4f}, real distance={real_distance}")
                break
    cv2.destroyWindow("Calibration")

    # Fit linear calibration
    coeffs = np.polyfit(calibration_depths, calibration_distances, 1)
    a, b = coeffs
    print(f"Calibration mapping: real_distance = {a:.4f}*depth + {b:.4f}")

    # Save for future use
    with open(calibration_file, "w") as f:
        json.dump({"a": a, "b": b}, f)
    print(f"✅ Calibration saved to {calibration_file}")

# ----------------------------
# Temporal smoothing setup
# ----------------------------
N = 3  # number of frames to average
depth_history = []

# Target frame size for speed
target_width, target_height = 320, 240

# ----------------------------
# Main loop
# ----------------------------
while True:
    start_time = time.time()

    ret, frame = cap.read()
    if not ret:
        continue

    # Resize for faster inference
    frame_small = cv2.resize(frame, (target_width, target_height))
    frame_rgb = cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(frame_rgb)

    # Preprocess
    inputs = processor(images=image, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # Forward pass
    with torch.no_grad():
        depth = model(**inputs).predicted_depth.squeeze().cpu().numpy()

    # Convert to metric depth using calibration
    depth_metric = a * depth + b

    # Temporal smoothing
    depth_history.append(depth_metric)
    if len(depth_history) > N:
        depth_history.pop(0)
    depth_smooth = sum(depth_history) / len(depth_history)

    # Gaussian smoothing
    depth_smooth = cv2.GaussianBlur(depth_smooth, (5, 5), 0)

    # Upscale depth map for visualization
    depth_display = cv2.resize(depth_smooth, (frame.shape[1], frame.shape[0]))
    depth_display_norm = np.clip(depth_display / depth_display.max(), 0, 1)
    depth_display_uint8 = (depth_display_norm * 255).astype(np.uint8)

    # Distance info
    h, w = depth_display.shape
    center_region = depth_display[h // 2 - 5:h // 2 + 5, w // 2 - 5:w // 2 + 5]
    center_distance = center_region.mean()
    closest_distance = depth_display.min()

    # Overlay info
    cv2.putText(frame, f"Center: {center_distance:.2f} m", (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Closest: {closest_distance:.2f} m", (30, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # FPS
    end_time = time.time()
    fps = 1 / (end_time - start_time)
    cv2.putText(frame, f"FPS: {fps:.1f}", (30, 130),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Show frames
    cv2.imshow("Camera Feed", frame)
    cv2.imshow("Depth Map (meters)", depth_display_uint8)

    # ESC to quit
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
