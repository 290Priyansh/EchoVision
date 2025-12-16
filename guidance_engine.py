"""
Guidance Engine Module
Generates directional instructions based on CENTER-FIRST navigation strategy
"""

import config
import languages
import numpy as np


class GuidanceEngine:
    """Generates navigation guidance messages using CENTER-FIRST strategy"""

    def __init__(self):
        """Initialize guidance engine"""
        self.last_guidance = None
        self.guidance_history = []
        self.max_history = 5
        self.current_language = config.DEFAULT_LANGUAGE

    def set_language(self, language_code):
        """Set current language for guidance generation"""
        self.current_language = language_code

    def generate_guidance(self, analysis_result, depth_map=None, center_of_mass=None):
        """
        Generate navigation guidance using CENTER-FIRST strategy

        Strategy:
        1. If CENTER is clear (< 10% occupancy) → Path clear (safe to walk)
        2. If CENTER is blocked (>= 10% occupancy) → Alert immediately
        3. If only SIDES have objects → Only alert if MAJOR presence (> 40%)

        Args:
            analysis_result: Dictionary from RegionAnalyzer.analyze_mask()
            depth_map: Optional depth map for distance estimation
            center_of_mass: Optional (x, y) tuple for precise positioning

        Returns:
            Dictionary with guidance information
        """
        # Check if any objects detected
        total_pixels = analysis_result['total_object_pixels']

        # Quick exit if nothing detected
        if total_pixels == 0:
            return self._create_clear_message()

        # Check frame percentage (failsafe for noise)
        frame_size = 640 * 480
        object_percentage = (total_pixels / frame_size) * 100

        if object_percentage < config.PATH_CLEAR_THRESHOLD:
            return self._create_clear_message()

        # Get occupancy for each region
        left_occ = analysis_result['occupancy'][0]
        center_occ = analysis_result['occupancy'][1]
        right_occ = analysis_result['occupancy'][2]

        # Debug print (optional - comment out in production)
        # print(f"[GUIDANCE] Occupancy: L={left_occ:.1f}% C={center_occ:.1f}% R={right_occ:.1f}%")

        # ============================================
        # STRATEGY 1: Check if CENTER is clear
        # ============================================
        if center_occ < config.CENTER_CLEAR_THRESHOLD:
            # Center is clear - check if sides are dangerously full

            if left_occ > config.SIDE_ALERT_THRESHOLD:
                # Left side has major presence
                direction = "right"
                angle = config.TURN_ANGLE_SMALL
                direction_text = languages.get_translation(self.current_language, 'right')
                message = languages.get_translation(
                    self.current_language,
                    'object_left_side_keep',
                    direction=direction_text
                )

                return {
                    'message': message,
                    'direction': direction,
                    'angle': angle,
                    'urgency': 'low',
                    'primary_region': 'LEFT',
                    'detected_regions': analysis_result['detected_regions']
                }

            if right_occ > config.SIDE_ALERT_THRESHOLD:
                # Right side has major presence
                direction = "left"
                angle = config.TURN_ANGLE_SMALL
                direction_text = languages.get_translation(self.current_language, 'left')
                message = languages.get_translation(
                    self.current_language,
                    'object_right_side_keep',
                    direction=direction_text
                )

                return {
                    'message': message,
                    'direction': direction,
                    'angle': angle,
                    'urgency': 'low',
                    'primary_region': 'RIGHT',
                    'detected_regions': analysis_result['detected_regions']
                }

            # Center clear, sides not concerning - PATH IS SAFE
            guidance = self._create_clear_message()
            guidance['detected_regions'] = analysis_result['detected_regions']
            return guidance

        # ============================================
        # STRATEGY 2: CENTER is BLOCKED - Priority Alert!
        # ============================================

        # Center has significant object presence - determine best direction
        if left_occ < right_occ:
            # More space on left, go left
            if left_occ < config.CENTER_CLEAR_THRESHOLD:
                # Left is clear
                angle = config.TURN_ANGLE_MEDIUM
                direction = "left"
                direction_text = languages.get_translation(self.current_language, 'left')
                message = languages.get_translation(
                    self.current_language,
                    'object_ahead',
                    direction=direction_text,
                    angle=angle
                )
                urgency = 'high'
            else:
                # Left also has objects, but less than right
                angle = config.TURN_ANGLE_LARGE
                direction = "left"
                direction_text = languages.get_translation(self.current_language, 'left')
                message = languages.get_translation(
                    self.current_language,
                    'object_ahead_both',
                    direction=direction_text,
                    angle=angle
                )
                urgency = 'high'

        elif right_occ < left_occ:
            # More space on right, go right
            if right_occ < config.CENTER_CLEAR_THRESHOLD:
                # Right is clear
                angle = config.TURN_ANGLE_MEDIUM
                direction = "right"
                direction_text = languages.get_translation(self.current_language, 'right')
                message = languages.get_translation(
                    self.current_language,
                    'object_ahead',
                    direction=direction_text,
                    angle=angle
                )
                urgency = 'high'
            else:
                # Right also has objects, but less than left
                angle = config.TURN_ANGLE_LARGE
                direction = "right"
                direction_text = languages.get_translation(self.current_language, 'right')
                message = languages.get_translation(
                    self.current_language,
                    'object_ahead_both',
                    direction=direction_text,
                    angle=angle
                )
                urgency = 'high'

        else:
            # Both sides equally blocked - CRITICAL
            angle = config.TURN_ANGLE_LARGE
            direction = "stop"
            message = languages.get_translation(
                self.current_language,
                'object_ahead_stop',
                angle=angle
            )
            urgency = 'critical'

        guidance = {
            'message': message,
            'direction': direction,
            'angle': angle,
            'urgency': urgency,
            'primary_region': 'CENTER',
            'detected_regions': analysis_result['detected_regions']
        }

        # Store in history
        self._add_to_history(guidance)

        return guidance

    def _create_clear_message(self):
        """Create message for clear path (SILENT)"""
        return {
            'message': languages.get_translation(self.current_language, 'path_clear'),
            'direction': None,
            'angle': 0,
            'urgency': 'none',
            'primary_region': None,
            'detected_regions': []
        }

    def _add_to_history(self, guidance):
        """Add guidance to history for analysis"""
        self.guidance_history.append(guidance)
        if len(self.guidance_history) > self.max_history:
            self.guidance_history.pop(0)
        self.last_guidance = guidance

    def get_guidance_summary(self):
        """Get summary of recent guidance"""
        if not self.guidance_history:
            return {
                'total_messages': 0,
                'most_common_direction': None,
                'average_angle': 0
            }

        directions = [g['direction'] for g in self.guidance_history if g['direction']]
        angles = [g['angle'] for g in self.guidance_history]

        most_common = max(set(directions), key=directions.count) if directions else None
        avg_angle = np.mean(angles) if angles else 0

        return {
            'total_messages': len(self.guidance_history),
            'most_common_direction': most_common,
            'average_angle': avg_angle
        }

    def clear_history(self):
        """Clear guidance history"""
        self.guidance_history = []
        self.last_guidance = None