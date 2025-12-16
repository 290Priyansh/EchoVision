"""
Visualizer Module
Handles all visual overlays, alerts, and information display
"""

import cv2
import numpy as np
import config


class Visualizer:
    """Manages visual overlays and display elements"""

    def __init__(self, frame_width, frame_height):
        """
        Initialize visualizer

        Args:
            frame_width: Width of video frame
            frame_height: Height of video frame
        """
        self.frame_width = frame_width
        self.frame_height = frame_height

    def create_alert_overlay(self, frame, mask, alert_color=None, alpha=None):
        """
        Create a colored overlay for detected objects

        Args:
            frame: BGR image
            mask: Binary mask (1 = object, 0 = background)
            alert_color: BGR color tuple (uses config default if None)
            alpha: Transparency 0.0-1.0 (uses config default if None)

        Returns:
            Frame with colored overlay applied
        """
        if alert_color is None:
            alert_color = config.ALERT_COLOR
        if alpha is None:
            alpha = config.ALERT_ALPHA

        # Create overlay
        overlay = frame.copy()

        # Create colored layer
        color_layer = np.zeros_like(frame)
        color_layer[:] = alert_color

        # Apply color only where mask is active
        if np.sum(mask) > 0:
            roi = overlay[mask == 1]
            if roi.size > 0:
                blended_roi = cv2.addWeighted(
                    roi, 1 - alpha,
                    color_layer[mask == 1], alpha,
                    0
                )
                overlay[mask == 1] = blended_roi

        return overlay

    def draw_guidance_message(self, frame, guidance, y_position=None):
        """
        Draw guidance message on frame

        Args:
            frame: BGR image to draw on
            guidance: Guidance dictionary from GuidanceEngine
            y_position: Y position for text (uses default if None)

        Returns:
            Frame with guidance message drawn
        """
        output = frame.copy()

        if y_position is None:
            y_position = self.frame_height - 80

        message = guidance['message']
        urgency = guidance.get('urgency', 'medium')

        # Set color based on urgency
        if urgency == 'critical':
            color = (0, 0, 255)  # Red
            thickness = 3
        elif urgency == 'high':
            color = (0, 165, 255)  # Orange
            thickness = 2
        elif urgency == 'medium':
            color = (0, 255, 255)  # Yellow
            thickness = 2
        else:
            color = (0, 255, 0)  # Green
            thickness = 2

        # Draw text background
        text_size = cv2.getTextSize(
            message,
            config.FONT,
            config.FONT_SCALE,
            thickness
        )[0]

        bg_x1 = 10
        bg_y1 = y_position - text_size[1] - 10
        bg_x2 = bg_x1 + text_size[0] + 20
        bg_y2 = y_position + 10

        cv2.rectangle(output, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 0, 0), -1)
        cv2.rectangle(output, (bg_x1, bg_y1), (bg_x2, bg_y2), color, 2)

        # Draw text
        cv2.putText(
            output, message,
            (20, y_position),
            config.FONT,
            config.FONT_SCALE,
            color,
            thickness
        )

        return output

    def draw_status_info(self, frame, fps, threshold, system_active=True):
        """
        Draw system status information

        Args:
            frame: BGR image to draw on
            fps: Current FPS
            threshold: Current depth threshold
            system_active: Whether system is actively detecting

        Returns:
            Frame with status info drawn
        """
        output = frame.copy()
        y_pos = 30

        # System status
        status = "ACTIVE" if system_active else "PAUSED"
        status_color = (0, 255, 0) if system_active else (0, 0, 255)
        cv2.putText(
            output, f"Status: {status}",
            (10, y_pos),
            config.FONT, config.FONT_SCALE,
            status_color, config.FONT_THICKNESS
        )

        # FPS
        y_pos += 30
        fps_color = (0, 255, 0) if fps >= 20 else (0, 165, 255)
        cv2.putText(
            output, f"FPS: {fps:.1f}",
            (10, y_pos),
            config.FONT, config.FONT_SCALE,
            fps_color, config.FONT_THICKNESS
        )

        # Threshold
        y_pos += 30
        cv2.putText(
            output, f"Threshold: {threshold:.2f}",
            (10, y_pos),
            config.FONT, config.FONT_SCALE,
            config.TEXT_COLOR, config.FONT_THICKNESS
        )

        return output

    def draw_center_of_mass(self, frame, center_point, color=(0, 255, 255)):
        """
        Draw center of mass indicator

        Args:
            frame: BGR image to draw on
            center_point: Tuple (x, y)
            color: Circle color (BGR)

        Returns:
            Frame with center of mass drawn
        """
        if center_point is None:
            return frame

        output = frame.copy()
        x, y = center_point

        # Draw crosshair
        cv2.circle(output, (x, y), 10, color, 2)
        cv2.line(output, (x - 20, y), (x + 20, y), color, 2)
        cv2.line(output, (x, y - 20), (x, y + 20), color, 2)

        return output

    def draw_depth_colormap(self, depth_map):
        """
        Convert depth map to colored visualization

        Args:
            depth_map: Normalized depth map (0.0 - 1.0)

        Returns:
            BGR colored depth visualization
        """
        # Convert to 8-bit
        depth_8bit = (depth_map * 255).astype(np.uint8)

        # Apply colormap (COLORMAP_TURBO: blue=close, red=far)
        depth_colored = cv2.applyColorMap(depth_8bit, cv2.COLORMAP_TURBO)

        return depth_colored

    def create_split_view(self, original_frame, depth_frame):
        """
        Create side-by-side view of original and depth

        Args:
            original_frame: Original BGR frame
            depth_frame: Depth visualization frame

        Returns:
            Combined frame with both views
        """
        # Resize both to half width
        h, w = original_frame.shape[:2]
        half_w = w // 2

        left = cv2.resize(original_frame, (half_w, h))
        right = cv2.resize(depth_frame, (half_w, h))

        # Concatenate horizontally
        combined = np.hstack([left, right])

        # Add labels
        cv2.putText(
            combined, "Original",
            (10, 30),
            config.FONT, config.FONT_SCALE,
            (255, 255, 255), config.FONT_THICKNESS
        )
        cv2.putText(
            combined, "Depth Map",
            (half_w + 10, 30),
            config.FONT, config.FONT_SCALE,
            (255, 255, 255), config.FONT_THICKNESS
        )

        return combined

    def draw_detection_statistics(self, frame, analysis_result):
        """
        Draw detection statistics overlay

        Args:
            frame: BGR image to draw on
            analysis_result: Region analysis result

        Returns:
            Frame with statistics drawn
        """
        output = frame.copy()

        # Position in top-right corner
        # Reduced width from 250 to 160
        box_width = 160
        x_pos = self.frame_width - box_width
        y_pos = 15
        
        # Reduced font scale from 0.6/0.5 to 0.4
        font_scale = 0.4
        line_height = 15

        # Background (tight fit)
        cv2.rectangle(
            output,
            (x_pos - 5, y_pos - 15),
            (self.frame_width - 5, y_pos + (6 * line_height) + 5),
            (0, 0, 0),
            -1
        )

        # Draw statistics
        cv2.putText(
            output, "Stats:",
            (x_pos, y_pos),
            config.FONT, font_scale,
            (255, 255, 255), 1
        )

        y_pos += line_height
        cv2.putText(
            output, f"Pixels: {analysis_result['total_object_pixels']}",
            (x_pos, y_pos),
            config.FONT, font_scale,
            (200, 200, 200), 1
        )

        y_pos += line_height
        for i, region_name in enumerate(config.REGION_NAMES):
            occ = analysis_result['occupancy'][i]
            # Abbreviate region names: LEFT -> L, CENTER -> C, RIGHT -> R
            short_name = region_name[0]
            cv2.putText(
                output, f"{short_name}: {occ:.1f}%",
                (x_pos, y_pos),
                config.FONT, font_scale,
                (200, 200, 200), 1
            )
            y_pos += line_height

        y_pos += 5
        detected = ", ".join([r[0] for r in analysis_result['detected_regions']]) or "-"
        cv2.putText(
            output, f"Act: {detected}",
            (x_pos, y_pos),
            config.FONT, font_scale,
            (0, 255, 0), 1
        )

        return output