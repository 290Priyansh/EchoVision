"""
Guidance Engine Module
Generates directional instructions based on object detection and region analysis
"""

import config
import numpy as np


class GuidanceEngine:
    """Generates navigation guidance messages"""

    def __init__(self):
        """Initialize guidance engine"""
        self.last_guidance = None
        self.guidance_history = []
        self.max_history = 5

    def generate_guidance(self, analysis_result, depth_map=None, center_of_mass=None):
        """
        Generate navigation guidance based on region analysis

        Args:
            analysis_result: Dictionary from RegionAnalyzer.analyze_mask()
            depth_map: Optional depth map for distance estimation
            center_of_mass: Optional (x, y) tuple for precise positioning

        Returns:
            Dictionary with guidance information:
            {
                'message': str,
                'direction': str,
                'angle': int,
                'urgency': str,
                'detected_regions': list
            }
        """
        # No objects detected
        if not analysis_result['detected_regions']:
            return self._create_clear_message()

        # Determine primary region and guidance
        primary_region = analysis_result['primary_region']
        detected_regions = analysis_result['detected_regions']

        # Generate guidance based on primary region
        if primary_region == "CENTER":
            guidance = self._generate_center_guidance(analysis_result, depth_map)
        elif primary_region == "LEFT":
            guidance = self._generate_left_guidance(analysis_result, depth_map)
        elif primary_region == "RIGHT":
            guidance = self._generate_right_guidance(analysis_result, depth_map)
        else:
            guidance = self._create_clear_message()

        # Add detected regions info
        guidance['detected_regions'] = detected_regions

        # Store in history
        self._add_to_history(guidance)

        return guidance

    def _generate_center_guidance(self, analysis_result, depth_map):
        """Generate guidance for objects in center region"""
        occupancy = analysis_result['occupancy']
        center_occ = occupancy[1]  # Index 1 is CENTER

        # Check if object also occupies left or right
        left_occ = occupancy[0]
        right_occ = occupancy[2]

        # Determine if object is slightly off-center
        if left_occ > config.MIN_OBJECT_OCCUPANCY_PERCENT and left_occ > right_occ:
            # Object slightly in left and center
            direction = "right"
            angle = config.TURN_ANGLE_SMALL
            message = f"Object ahead and slightly left, move {direction} by {angle} degrees"
        elif right_occ > config.MIN_OBJECT_OCCUPANCY_PERCENT and right_occ > left_occ:
            # Object slightly in right and center
            direction = "left"
            angle = config.TURN_ANGLE_SMALL
            message = f"Object ahead and slightly right, move {direction} by {angle} degrees"
        else:
            # Object directly ahead
            direction = "left or right"
            angle = config.TURN_ANGLE_MEDIUM
            message = f"Object directly ahead, move {direction} by {angle} degrees"

        # Determine urgency based on depth
        urgency = self._calculate_urgency(depth_map, analysis_result)

        return {
            'message': message,
            'direction': direction,
            'angle': angle,
            'urgency': urgency,
            'primary_region': 'CENTER'
        }

    def _generate_left_guidance(self, analysis_result, depth_map):
        """Generate guidance for objects in left region"""
        occupancy = analysis_result['occupancy']
        left_occ = occupancy[0]
        center_occ = occupancy[1]

        # Determine angle based on how much is in left vs center
        if center_occ > config.MIN_OBJECT_OCCUPANCY_PERCENT:
            # Object spans left and center
            angle = config.TURN_ANGLE_MEDIUM
            message = f"Object detected on left side, move right by {angle} degrees"
        else:
            # Object mostly in left
            angle = config.TURN_ANGLE_LARGE
            message = f"Object detected on left, move right by {angle} degrees"

        urgency = self._calculate_urgency(depth_map, analysis_result)

        return {
            'message': message,
            'direction': 'right',
            'angle': angle,
            'urgency': urgency,
            'primary_region': 'LEFT'
        }

    def _generate_right_guidance(self, analysis_result, depth_map):
        """Generate guidance for objects in right region"""
        occupancy = analysis_result['occupancy']
        right_occ = occupancy[2]
        center_occ = occupancy[1]

        # Determine angle based on how much is in right vs center
        if center_occ > config.MIN_OBJECT_OCCUPANCY_PERCENT:
            # Object spans right and center
            angle = config.TURN_ANGLE_MEDIUM
            message = f"Object detected on right side, move left by {angle} degrees"
        else:
            # Object mostly in right
            angle = config.TURN_ANGLE_LARGE
            message = f"Object detected on right, move left by {angle} degrees"

        urgency = self._calculate_urgency(depth_map, analysis_result)

        return {
            'message': message,
            'direction': 'left',
            'angle': angle,
            'urgency': urgency,
            'primary_region': 'RIGHT'
        }

    def _create_clear_message(self):
        """Create message for clear path"""
        return {
            'message': "Path clear",
            'direction': None,
            'angle': 0,
            'urgency': 'none',
            'primary_region': None,
            'detected_regions': []
        }

    def _calculate_urgency(self, depth_map, analysis_result):
        """
        Calculate urgency level based on object proximity

        Args:
            depth_map: Normalized depth map
            analysis_result: Region analysis result

        Returns:
            Urgency level: "critical", "high", "medium", "low"
        """
        if depth_map is None:
            return "medium"

        # Get depth values only where objects exist
        total_pixels = analysis_result['total_object_pixels']
        if total_pixels == 0:
            return "low"

        # Calculate average depth of detected objects
        # Since we're working with a mask, we need to extract depth values
        # This is simplified - in practice, pass the mask to this function

        # For now, use threshold-based urgency
        if analysis_result['total_object_pixels'] > 50000:
            # Large object detected
            return "high"
        elif analysis_result['total_object_pixels'] > 20000:
            return "medium"
        else:
            return "low"

    def _add_to_history(self, guidance):
        """Add guidance to history for analysis"""
        self.guidance_history.append(guidance)
        if len(self.guidance_history) > self.max_history:
            self.guidance_history.pop(0)
        self.last_guidance = guidance

    def get_guidance_summary(self):
        """
        Get summary of recent guidance

        Returns:
            Dictionary with summary statistics
        """
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