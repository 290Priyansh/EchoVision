"""
Depth Estimation Module
Handles depth map generation and normalization using Depth-Anything V2
"""

import cv2
import torch
import numpy as np
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForDepthEstimation
import warnings
import config

warnings.filterwarnings('ignore')


class DepthEstimator:
    """Handles depth estimation using Depth-Anything V2 model"""

    def __init__(self):
        """Initialize the depth estimation model"""
        self.processor = None
        self.model = None
        self.device = None
        self.depth_history = []
        self.initialized = False

    def initialize(self):
        """Load and initialize the model"""
        print(f"Loading {config.MODEL_NAME}...")

        self.processor = AutoImageProcessor.from_pretrained(
            config.MODEL_NAME,
            use_fast=True
        )
        self.model = AutoModelForDepthEstimation.from_pretrained(
            config.MODEL_NAME
        )

        # Determine device
        if config.DEVICE == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = config.DEVICE

        self.model.to(self.device)
        self.model.eval()

        self.initialized = True
        print(f"✅ Model loaded on {self.device}")

    def normalize_depth(self, depth_map):
        """
        Normalize depth map to 0-1 range.

        Args:
            depth_map: Raw depth map from model

        Returns:
            Normalized depth map where 0.0 = closest, 1.0 = farthest
        """
        depth_min = depth_map.min()
        depth_max = depth_map.max()
        # NEW: Safety check - if range is too narrow, something is wrong
        depth_range = depth_max - depth_min

        if depth_range < 0.01:  # Very narrow range
            # Return all "far" - scene is too uniform
            print("  [WARNING] Depth range too narrow, returning 'far' map")
            return np.ones_like(depth_map)

        if depth_max - depth_min > 0:
            # Standard normalization
            normalized = (depth_map - depth_min) / (depth_max - depth_min)

            # Depth Anything outputs disparity (high value = close)
            # Invert so that 0.0 = close, 1.0 = far
            normalized = 1.0 - normalized
        else:
            normalized = np.zeros_like(depth_map)

        return normalized

    def apply_temporal_smoothing(self, depth_map):
        """
        Apply temporal smoothing to reduce flickering

        Args:
            depth_map: Current frame's depth map

        Returns:
            Smoothed depth map averaged over recent frames
        """
        self.depth_history.append(depth_map)

        if len(self.depth_history) > config.SMOOTHING_FRAMES:
            self.depth_history.pop(0)

        return np.mean(self.depth_history, axis=0)

    def estimate_depth(self, frame):
        """
        Estimate depth from a single frame

        Args:
            frame: BGR image from camera (numpy array)

        Returns:
            Normalized and smoothed depth map (0.0 = close, 1.0 = far)
        """

        if not self.initialized:
            raise RuntimeError("DepthEstimator not initialized. Call initialize() first.")

        # Resize for faster inference
        frame_small = cv2.resize(
            frame,
            (config.INFERENCE_WIDTH, config.INFERENCE_HEIGHT)
        )

        # Convert BGR to RGB and create PIL image
        pil_image = Image.fromarray(cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB))

        # Prepare inputs
        inputs = self.processor(images=pil_image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Run inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            depth_map = outputs.predicted_depth.squeeze().cpu().numpy()
        depth_variance = np.var(depth_map)

        if depth_variance < config.MIN_DEPTH_VARIANCE:
            # Uniform scene - return all far
            depth_smooth = np.ones_like(depth_map)

        # Normalize depth
        depth_norm = self.normalize_depth(depth_map)

        # Apply temporal smoothing
        depth_smooth = self.apply_temporal_smoothing(depth_norm)

        # Resize to match original frame dimensions
        depth_resized = cv2.resize(
            depth_smooth,
            (frame.shape[1], frame.shape[0]),
            interpolation=cv2.INTER_LINEAR
        )

        return depth_resized

    def get_close_objects_mask(self, depth_map, threshold=None):
        """
        Generate a binary mask of objects closer than threshold

        Args:
            depth_map: Normalized depth map
            threshold: Distance threshold (uses config default if None)

        Returns:
            Binary mask where 1 = close object, 0 = far/background
        """
        if threshold is None:
            threshold = config.CLOSE_OBJECT_THRESHOLD

        # Objects with depth < threshold are considered close
        mask = (depth_map < threshold).astype(np.uint8)

        return mask

    def get_distance_category(self, depth_value):
        """
        Categorize a depth value into distance categories

        Args:
            depth_value: Normalized depth (0.0 - 1.0)

        Returns:
            String category: "very_close", "close", "moderate", or "far"
        """
        if depth_value < config.DISTANCE_VERY_CLOSE:
            return "very_close"
        elif depth_value < config.DISTANCE_CLOSE:
            return "close"
        elif depth_value < config.DISTANCE_MODERATE:
            return "moderate"
        else:
            return "far"

    def reset_history(self):
        """Clear depth history (useful when restarting)"""
        self.depth_history = []