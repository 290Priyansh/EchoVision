"""
Region Analyzer Module
Divides screen into regions and analyzes object distribution
"""

import numpy as np
import cv2
import config


class RegionAnalyzer:
    """Analyzes object distribution across screen regions"""

    def __init__(self, frame_width, frame_height):
        """
        Initialize region analyzer

        Args:
            frame_width: Width of video frame
            frame_height: Height of video frame
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.num_regions = config.NUM_REGIONS

        # Calculate region boundaries for landscape orientation
        # Divide frame into vertical strips (left, center, right)
        self.region_width = frame_width // self.num_regions
        self.region_boundaries = self._calculate_boundaries()

    def _calculate_boundaries(self):
        """
        Calculate pixel boundaries for each region

        Returns:
            List of tuples [(x_start, x_end), ...]
        """
        boundaries = []
        for i in range(self.num_regions):
            x_start = i * self.region_width
            x_end = (i + 1) * self.region_width if i < self.num_regions - 1 else self.frame_width
            boundaries.append((x_start, x_end))

        return boundaries

    def get_region_name(self, region_index):
        """
        Get name of region by index

        Args:
            region_index: Index (0, 1, 2)

        Returns:
            Region name string
        """
        if 0 <= region_index < len(config.REGION_NAMES):
            return config.REGION_NAMES[region_index]
        return "UNKNOWN"

    def analyze_mask(self, mask):
        """
        Analyze a binary mask to determine object distribution across regions

        Args:
            mask: Binary mask (1 = object, 0 = background)

        Returns:
            Dictionary with region analysis:
            {
                'occupancy': [left_%, center_%, right_%],  # % of REGION covered
                'total_object_pixels': int,
                'detected_regions': [region_names],
                'primary_region': region_name,
                'region_pixel_counts': [pixels in each region]
            }
        """
        # Count total object pixels
        total_object_pixels = np.sum(mask)

        # NEW: Ignore if too few pixels (noise filter)
        if total_object_pixels < config.MIN_OBJECT_PIXELS:
            return {
                'occupancy': [0.0, 0.0, 0.0],
                'total_object_pixels': 0,
                'detected_regions': [],
                'primary_region': None,
                'region_pixel_counts': [0, 0, 0]
            }

        # Calculate occupancy for each region
        occupancy = []
        region_pixel_counts = []

        for x_start, x_end in self.region_boundaries:
            # Extract this region from the mask
            region_mask = mask[:, x_start:x_end]

            # Count object pixels in this region
            region_pixels = np.sum(region_mask)
            region_pixel_counts.append(region_pixels)

            # NEW: Calculate % of THIS REGION that is covered by objects
            region_width = x_end - x_start
            region_total_pixels = self.frame_height * region_width

            # Percentage of region covered
            occupancy_percent = (region_pixels / region_total_pixels) * 100.0
            occupancy.append(occupancy_percent)

        # Determine which regions have significant object presence
        detected_regions = []
        for i, occ in enumerate(occupancy):
            if occ >= config.MIN_OBJECT_OCCUPANCY_PERCENT:
                detected_regions.append(self.get_region_name(i))

        # Find primary region (highest coverage %)
        primary_region_idx = np.argmax(occupancy)
        primary_region = self.get_region_name(primary_region_idx)

        # Only consider it primary if it meets threshold
        if occupancy[primary_region_idx] < config.MIN_OBJECT_OCCUPANCY_PERCENT:
            primary_region = None

        return {
            'occupancy': occupancy,
            'total_object_pixels': int(total_object_pixels),
            'detected_regions': detected_regions,
            'primary_region': primary_region,
            'region_pixel_counts': region_pixel_counts
        }

    def get_center_of_mass(self, mask):
        """
        Calculate center of mass of detected objects

        Args:
            mask: Binary mask

        Returns:
            Tuple (x, y) of center of mass, or None if no objects
        """
        if np.sum(mask) == 0:
            return None

        # Calculate moments
        moments = cv2.moments(mask.astype(np.uint8))

        if moments['m00'] == 0:
            return None

        cx = int(moments['m10'] / moments['m00'])
        cy = int(moments['m01'] / moments['m00'])

        return (cx, cy)

    def get_region_at_point(self, x, y):
        """
        Determine which region contains a given point

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Region index (0, 1, 2)
        """
        for i, (x_start, x_end) in enumerate(self.region_boundaries):
            if x_start <= x < x_end:
                return i

        # Default to last region if out of bounds
        return self.num_regions - 1

    def draw_region_boundaries(self, frame, color=(255, 255, 255), thickness=2):
        """
        Draw region boundaries on frame for visualization

        Args:
            frame: BGR image to draw on
            color: Line color (BGR)
            thickness: Line thickness

        Returns:
            Frame with boundaries drawn
        """
        output = frame.copy()

        for i in range(1, self.num_regions):
            x = i * self.region_width
            cv2.line(output, (x, 0), (x, self.frame_height), color, thickness)

        # Label regions
        for i, (x_start, x_end) in enumerate(self.region_boundaries):
            label = self.get_region_name(i)
            x_center = (x_start + x_end) // 2
            cv2.putText(
                output, label, (x_center - 40, 30),
                config.FONT, config.FONT_SCALE,
                color, config.FONT_THICKNESS
            )

        return output

    def draw_occupancy_bars(self, frame, analysis_result):
        """
        Draw visual bars showing occupancy percentage per region

        Args:
            frame: BGR image to draw on
            analysis_result: Result from analyze_mask()

        Returns:
            Frame with occupancy bars drawn
        """
        output = frame.copy()
        bar_height = 20
        bar_y = self.frame_height - 40

        for i, occupancy in enumerate(analysis_result['occupancy']):
            x_start, x_end = self.region_boundaries[i]
            region_width = x_end - x_start

            # Draw background bar
            cv2.rectangle(
                output,
                (x_start + 5, bar_y),
                (x_end - 5, bar_y + bar_height),
                (50, 50, 50),
                -1
            )

            # Draw occupancy bar
            fill_width = int((region_width - 10) * occupancy / 100.0)
            if fill_width > 0:
                cv2.rectangle(
                    output,
                    (x_start + 5, bar_y),
                    (x_start + 5 + fill_width, bar_y + bar_height),
                    (0, 255, 0),
                    -1
                )

            # Draw percentage text
            text = f"{occupancy:.0f}%"
            cv2.putText(
                output, text,
                (x_start + 10, bar_y + 15),
                config.FONT, 0.5,
                (255, 255, 255), 1
            )

        return output