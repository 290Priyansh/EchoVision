"""
Video Capture Module
Handles camera initialization and frame capture
"""

import cv2
import config
import time


class VideoCapture:
    """Manages video capture from camera"""

    def __init__(self):
        """Initialize video capture"""
        self.cap = None
        self.is_opened_flag = False
        self.frame_count = 0

    def is_opened(self):
        """Check if camera is opened"""
        return self.is_opened_flag

    def _init_fps_counters(self):
        """Initialize FPS counters"""
        self.fps = 0
        self.last_fps_time = time.time()
        self.fps_frame_count = 0

    def initialize(self, camera_index=None):
        """
        Initialize camera

        Args:
            camera_index: Camera index (uses config default if None)

        Returns:
            True if successful, False otherwise
        """
        if camera_index is None:
            camera_index = config.CAMERA_INDEX

        print(f"Initializing camera {camera_index}...")

        self.cap = cv2.VideoCapture(camera_index)

        if not self.cap.isOpened():
            print(f" Failed to open camera {camera_index}")
            return False

        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

        # Verify settings
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print(f" Camera initialized: {actual_width}x{actual_height}")

        self._init_fps_counters()
        self.is_opened_flag = True
        return True

    def read_frame(self):
        """
        Read a single frame from camera

        Returns:
            Tuple (success, frame) where:
            - success: Boolean indicating if frame was read
            - frame: BGR image as numpy array, or None if failed
        """
        if not self.is_opened_flag:
            return False, None

        ret, frame = self.cap.read()
        frame = cv2.flip(frame,1)

        if ret and frame is not None:
            frame = cv2.flip(frame, 1)
            self.frame_count += 1
            self.fps_frame_count += 1
            self._update_fps()
        
        return ret, frame

    def _update_fps(self):
        """Update FPS calculation"""
        current_time = time.time()
        elapsed = current_time - self.last_fps_time

        if elapsed >= 1.0:  # Update every second
            self.fps = self.fps_frame_count / elapsed
            self.fps_frame_count = 0
            self.last_fps_time = current_time

    def get_fps(self):
        """Get current FPS"""
        return self.fps

    def get_frame_dimensions(self):
        """
        Get current frame dimensions

        Returns:
            Tuple (width, height)
        """
        if not self.is_opened:
            return (0, 0)

        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        return (width, height)

    def release(self):
        """Release camera resources"""
        if self.cap is not None:
            self.cap.release()
            self.is_opened_flag = False
            print("Camera released")

    def __del__(self):
        """Destructor to ensure camera is released"""
        self.release()