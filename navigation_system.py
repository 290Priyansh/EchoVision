"""
Navigation System Module
Main controller that orchestrates all components
"""

import config
import time
from video_capture import VideoCapture
from depth_estimation import DepthEstimator
from region_analyzer import RegionAnalyzer
from guidance_engine import GuidanceEngine
from visualizer import Visualizer
from audio_feedback import AudioFeedback


class NavigationSystem:
    """Main navigation system controller"""

    def __init__(self):
        """Initialize navigation system"""
        self.video_capture = None
        self.depth_estimator = None
        self.region_analyzer = None
        self.guidance_engine = None
        self.visualizer = None
        self.audio_feedback = None  # Piper TTS audio

        self.is_initialized = False
        self.is_running = False

        # Current state
        self.current_frame = None
        self.current_depth = None
        self.current_mask = None
        self.current_analysis = None
        self.current_guidance = None

        # Settings
        self.current_threshold = config.CLOSE_OBJECT_THRESHOLD
        self.min_occupancy = config.MIN_OBJECT_OCCUPANCY_PERCENT

        # Audio timing
        self.last_speech_time = 0
        self.last_spoken_message = None

    def initialize(self):
        """Initialize all system components"""
        print("\n" + "=" * 60)
        print("  BLIND NAVIGATION ASSISTANCE SYSTEM - Phase 1")
        print("=" * 60)

        try:
            # Initialize video capture
            print("\n[1/5] Initializing camera...")
            self.video_capture = VideoCapture()
            if not self.video_capture.initialize():
                return False

            # Get frame dimensions
            width, height = self.video_capture.get_frame_dimensions()

            # Initialize depth estimator
            print("\n[2/5] Loading depth estimation model...")
            self.depth_estimator = DepthEstimator()
            self.depth_estimator.initialize()

            # Initialize region analyzer
            print("\n[3/5] Setting up region analyzer...")
            self.region_analyzer = RegionAnalyzer(width, height)
            print(f"✅ Regions configured: {config.REGION_NAMES}")

            # Initialize guidance engine
            print("\n[4/5] Initializing guidance engine...")
            self.guidance_engine = GuidanceEngine()
            print("✅ Guidance engine ready")

            # Initialize visualizer
            print("\n[5/6] Setting up visualizer...")
            self.visualizer = Visualizer(width, height)
            print("✅ Visualizer ready")

            # Initialize audio feedback (Piper TTS)
            if config.ENABLE_AUDIO:
                print("\n[6/6] Initializing Piper TTS audio...")
                self.audio_feedback = AudioFeedback()
                if not self.audio_feedback.initialize():
                    print("⚠️  Audio initialization failed - continuing without audio")
                    self.audio_feedback = None
            else:
                print("\n[6/6] Audio disabled in config")

            self.is_initialized = True

            print("\n" + "=" * 60)
            print("  ✅ SYSTEM INITIALIZED SUCCESSFULLY")
            print("=" * 60 + "\n")

            return True

        except Exception as e:
            print(f"\n❌ Initialization failed: {e}")
            return False

    def start(self):
        """Start the navigation system"""
        if not self.is_initialized:
            if not self.initialize():
                return False

        self.is_running = True

        # Announce start
        if self.audio_feedback:
            self.audio_feedback.speak_status("Detection started")

        print("Navigation system started")
        return True

    def stop(self):
        """Stop the navigation system"""
        self.is_running = False

        # Announce stop
        if self.audio_feedback:
            self.audio_feedback.speak_status("Detection stopped")

        if self.video_capture:
            self.video_capture.release()

        print("Navigation system stopped")

    def process_frame(self):
        """
        Process a single frame through the entire pipeline

        Returns:
            Dictionary containing all processing results
        """
        if not self.is_running:
            return None

        # Capture frame
        ret, frame = self.video_capture.read_frame()
        if not ret:
            return None

        self.current_frame = frame

        # Estimate depth
        depth_map = self.depth_estimator.estimate_depth(frame)
        self.current_depth = depth_map

        # Get close objects mask
        mask = self.depth_estimator.get_close_objects_mask(depth_map, self.current_threshold)
        self.current_mask = mask

        # Analyze regions
        analysis = self.region_analyzer.analyze_mask(mask)
        self.current_analysis = analysis

        # Get center of mass
        center_of_mass = self.region_analyzer.get_center_of_mass(mask)

        # Generate guidance
        guidance = self.guidance_engine.generate_guidance(analysis, depth_map, center_of_mass)
        self.current_guidance = guidance

        # Speak guidance if audio enabled
        if self.audio_feedback and config.ENABLE_AUDIO:
            self._handle_audio_guidance(guidance)

        return {
            'frame': frame,
            'depth_map': depth_map,
            'mask': mask,
            'analysis': analysis,
            'guidance': guidance,
            'center_of_mass': center_of_mass,
            'fps': self.video_capture.get_fps()
        }

    def _handle_audio_guidance(self, guidance):
        """
        Handle audio feedback for navigation guidance

        Args:
            guidance: Guidance dictionary from GuidanceEngine
        """
        if not self.audio_feedback:
            return

        # Use AudioFeedback's built-in cooldown and deduplication
        self.audio_feedback.speak_guidance(guidance)

    def get_display_frame(self, show_regions=True, show_stats=True, show_depth=False):
        """
        Get a frame with all visual overlays for display

        Args:
            show_regions: Show region boundaries
            show_stats: Show detection statistics
            show_depth: Show depth map instead of camera view

        Returns:
            Processed frame ready for display
        """
        # Process current frame
        result = self.process_frame()
        if result is None:
            return None

        frame = result['frame'].copy()

        # Show depth map view
        if show_depth:
            frame = self.visualizer.draw_depth_colormap(result['depth_map'])
        else:
            # Apply alert overlay for close objects
            frame = self.visualizer.create_alert_overlay(
                frame,
                result['mask']
            )

        # Draw region boundaries
        if show_regions:
            frame = self.region_analyzer.draw_region_boundaries(frame)

        # Draw occupancy bars
        frame = self.region_analyzer.draw_occupancy_bars(frame, result['analysis'])

        # Draw center of mass
        if result['center_of_mass']:
            frame = self.visualizer.draw_center_of_mass(frame, result['center_of_mass'])

        # Draw guidance message
        frame = self.visualizer.draw_guidance_message(frame, result['guidance'])

        # Draw status info
        frame = self.visualizer.draw_status_info(
            frame,
            result['fps'],
            self.current_threshold,
            self.is_running
        )

        # Draw statistics
        if show_stats:
            frame = self.visualizer.draw_detection_statistics(frame, result['analysis'])

        return frame

    def set_threshold(self, threshold):
        """Update detection threshold"""
        self.current_threshold = threshold
        config.CLOSE_OBJECT_THRESHOLD = threshold

    def set_min_occupancy(self, occupancy):
        """Update minimum occupancy percentage"""
        self.min_occupancy = occupancy
        config.MIN_OBJECT_OCCUPANCY_PERCENT = occupancy

    def get_current_guidance(self):
        """Get current guidance message"""
        return self.current_guidance

    def get_system_status(self):
        """
        Get current system status

        Returns:
            Dictionary with system status information
        """
        return {
            'initialized': self.is_initialized,
            'running': self.is_running,
            'fps': self.video_capture.get_fps() if self.video_capture else 0,
            'threshold': self.current_threshold,
            'min_occupancy': self.min_occupancy,
            'guidance': self.current_guidance
        }

    def cleanup(self):
        """Clean up system resources"""
        self.stop()

        # Shutdown audio
        if self.audio_feedback:
            self.audio_feedback.shutdown()

        print("System cleanup complete")