"""
Main Entry Point
Launches the Blind Navigation Assistance System
"""

import sys
import config
from navigation_system import NavigationSystem
from gui import NavigationGUI


def main():
    """Main application entry point"""
    print("\n" + "=" * 70)
    print("  BLIND NAVIGATION ASSISTANCE SYSTEM ")
    print("  Assistive Navigation with Real-time Object Detection")
    print("=" * 70)

    try:
        # Create navigation system
        nav_system = NavigationSystem()

        # Create and run GUI
        gui = NavigationGUI(nav_system)

        print("\n✅ GUI launched successfully")
        print("\nControls:")
        print("  - Click 'START DETECTION' to begin")
        print("  - Adjust sliders to tune sensitivity")
        print("  - Use preset buttons for quick configuration")
        print("  - Toggle checkboxes to show/hide overlays")
        print("\nSystem Configuration:")
        print(f"  - Frame Size: {config.FRAME_WIDTH}x{config.FRAME_HEIGHT}")
        print(f"  - Regions: {config.NUM_REGIONS} ({', '.join(config.REGION_NAMES)})")
        print(f"  - Default Threshold: {config.CLOSE_OBJECT_THRESHOLD}")
        print(f"  - Min Occupancy: {config.MIN_OBJECT_OCCUPANCY_PERCENT}%")
        print(f"  - Turn Angles: {config.TURN_ANGLE_SMALL}°, {config.TURN_ANGLE_MEDIUM}°, {config.TURN_ANGLE_LARGE}°")

        print("\n" + "=" * 70 + "\n")

        # Start GUI main loop
        gui.run()

    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nThank you for using the Blind Navigation Assistance System")
        print("=" * 70 + "\n")


if __name__ == "__main__":
    main()