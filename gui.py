"""
GUI Module
Tkinter-based graphical user interface for the navigation system
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import config
import languages


class NavigationGUI:
    """Main GUI window for navigation system"""

    def __init__(self, navigation_system):
        """
        Initialize GUI

        Args:
            navigation_system: Instance of NavigationSystem to control
        """
        self.nav_system = navigation_system
        self.root = tk.Tk()
        self.root.title(config.GUI_TITLE)
        self.root.geometry(f"{config.GUI_WIDTH}x{config.GUI_HEIGHT}")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.is_running = False
        self.current_frame = None
        self.update_job = None

        self._build_gui()

    def _build_gui(self):
        """Build GUI components"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Video display frame
        self._build_video_frame(main_frame)

        # Control panel
        self._build_control_panel(main_frame)

        # Status bar
        self._build_status_bar(main_frame)

    def _build_video_frame(self, parent):
        """Build video display area"""
        video_frame = ttk.LabelFrame(parent, text="Camera View", padding="5")
        video_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # Video canvas
        self.video_canvas = tk.Canvas(
            video_frame,
            width=640,
            height=480,
            bg='black'
        )
        self.video_canvas.pack(fill=tk.BOTH, expand=True)

        # Initialize overlay text items
        self.overlay_status = self.video_canvas.create_text(
            10, 10, anchor=tk.NW, fill="green", font=("Helvetica", 12, "bold"), text=""
        )
        self.overlay_fps = self.video_canvas.create_text(
            10, 30, anchor=tk.NW, fill="yellow", font=("Helvetica", 12, "bold"), text=""
        )
        self.overlay_info = self.video_canvas.create_text(
            10, 50, anchor=tk.NW, fill="purple", font=("Helvetica", 10), text=""
        )

    def _build_control_panel(self, parent):
        """Build control buttons and settings"""
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)

        # Start/Stop button
        self.start_button = tk.Button(
            control_frame,
            text="START DETECTION",
            command=self.toggle_detection,
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            bg='#4CAF50',
            fg='white',
            font=config.BUTTON_FONT
        )
        self.start_button.grid(row=0, column=0, padx=5, pady=5)

        # Sensitivity preset buttons
        ttk.Label(control_frame, text="Sensitivity:").grid(row=0, column=1, padx=10)

        sensitivity_frame = ttk.Frame(control_frame)
        sensitivity_frame.grid(row=0, column=2, padx=5)

        ttk.Button(
            sensitivity_frame,
            text="Low",
            command=lambda: self.set_sensitivity('low')
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            sensitivity_frame,
            text="Medium",
            command=lambda: self.set_sensitivity('medium')
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            sensitivity_frame,
            text="High",
            command=lambda: self.set_sensitivity('high')
        ).pack(side=tk.LEFT, padx=2)

        # Settings sliders
        settings_frame = ttk.Frame(control_frame)
        settings_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))

        # Threshold slider
        ttk.Label(settings_frame, text="Detection Threshold:").grid(row=0, column=0, sticky=tk.W)
        self.threshold_var = tk.DoubleVar(value=config.CLOSE_OBJECT_THRESHOLD)
        self.threshold_slider = ttk.Scale(
            settings_frame,
            from_=0.05,
            to=0.50,
            variable=self.threshold_var,
            orient=tk.HORIZONTAL,
            length=200,
            command=self.on_threshold_change
        )
        self.threshold_slider.grid(row=0, column=1, padx=10)
        self.threshold_label = ttk.Label(settings_frame, text=f"{config.CLOSE_OBJECT_THRESHOLD:.2f}")
        self.threshold_label.grid(row=0, column=2)

        # Occupancy slider
        ttk.Label(settings_frame, text="Min Occupancy %:").grid(row=1, column=0, sticky=tk.W)
        self.occupancy_var = tk.DoubleVar(value=config.MIN_OBJECT_OCCUPANCY_PERCENT)
        self.occupancy_slider = ttk.Scale(
            settings_frame,
            from_=5.0,
            to=50.0,
            variable=self.occupancy_var,
            orient=tk.HORIZONTAL,
            length=200,
            command=self.on_occupancy_change
        )
        self.occupancy_slider.grid(row=1, column=1, padx=10)
        self.occupancy_label = ttk.Label(settings_frame, text=f"{config.MIN_OBJECT_OCCUPANCY_PERCENT:.1f}%")
        self.occupancy_label.grid(row=1, column=2)

        # Debug options
        debug_frame = ttk.Frame(control_frame)
        debug_frame.grid(row=2, column=0, columnspan=3, pady=5)

        self.show_regions_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            debug_frame,
            text="Show Regions",
            variable=self.show_regions_var
        ).pack(side=tk.LEFT, padx=5)

        self.show_stats_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            debug_frame,
            text="Show Statistics",
            variable=self.show_stats_var
        ).pack(side=tk.LEFT, padx=5)

        self.show_depth_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            debug_frame,
            text="Show Depth Map",
            variable=self.show_depth_var
        ).pack(side=tk.LEFT, padx=5)

        # Audio controls
        self._build_audio_controls(control_frame)

    def _build_status_bar(self, parent):
        """Build status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)

        self.status_label = ttk.Label(
            status_frame,
            text="System Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X)

    def _build_audio_controls(self, parent):
        """Build audio feedback controls"""
        audio_frame = ttk.LabelFrame(parent, text="Audio Settings", padding="5")
        audio_frame.grid(row=3, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))

        # Enable/Disable audio
        self.audio_enabled_var = tk.BooleanVar(value=config.ENABLE_AUDIO)
        ttk.Checkbutton(
            audio_frame,
            text="Enable Voice Guidance",
            variable=self.audio_enabled_var,
            command=self.toggle_audio
        ).grid(row=0, column=0, columnspan=2, padx=5, sticky=tk.W)

        # Language selection frame
        lang_group = ttk.Frame(audio_frame)
        lang_group.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(lang_group, text="Language:").pack(side=tk.LEFT, padx=5)
        
        self.language_var = tk.StringVar(value=config.CURRENT_LANGUAGE)
        
        for lang_code, lang_name in languages.AVAILABLE_LANGUAGES.items():
            ttk.Radiobutton(
                lang_group,
                text=lang_name,
                variable=self.language_var,
                value=lang_code,
                command=self.on_language_change
            ).pack(side=tk.LEFT, padx=10)

        # Test audio button
        ttk.Button(
            audio_frame,
            text="Test Audio",
            command=self.test_audio
        ).grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        # Audio status
        self.audio_status_label = ttk.Label(
            audio_frame,
            text="Audio: Ready" if config.ENABLE_AUDIO else "Audio: Disabled",
            foreground="green" if config.ENABLE_AUDIO else "gray"
        )
        self.audio_status_label.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

    def toggle_audio(self):
        """Toggle audio on/off"""
        enabled = self.audio_enabled_var.get()
        config.ENABLE_AUDIO = enabled

        status_text = "Audio: Ready" if enabled else "Audio: Disabled"
        status_color = "green" if enabled else "gray"
        self.audio_status_label.config(text=status_text, foreground=status_color)

        if self.nav_system.audio_feedback:
            if enabled:
                self.nav_system.audio_feedback.speak_status("Audio enabled")
            else:
                self.nav_system.audio_feedback.speak_status("Audio disabled")

    def on_language_change(self):
        """Handle language change"""
        new_lang = self.language_var.get()
        if new_lang != config.CURRENT_LANGUAGE:
            self.nav_system.set_language(new_lang)
            # Update config to match
            config.CURRENT_LANGUAGE = new_lang

    def test_audio(self):
        """Test audio output"""
        if self.nav_system.audio_feedback:
            self.nav_system.audio_feedback.test_audio()
        else:
            messagebox.showwarning(
                "Audio Not Available",
                "Audio system not initialized. Check Piper model installation."
            )

    def toggle_detection(self):
        """Start or stop detection"""
        if not self.is_running:
            # Start detection
            if self.nav_system.start():
                self.is_running = True
                self.start_button.config(
                    text="STOP DETECTION",
                    bg='#f44336'
                )
                self.status_label.config(text="Detection Active")
                self.update_video()
            else:
                messagebox.showerror("Error", "Failed to start camera")
        else:
            # Stop detection
            self.nav_system.stop()
            self.is_running = False
            self.start_button.config(
                text="START DETECTION",
                bg='#4CAF50'
            )
            self.status_label.config(text="Detection Stopped")
            if self.update_job:
                self.root.after_cancel(self.update_job)
                self.update_job = None

    def update_video(self):
        """Update video display"""
        try:
            if not self.is_running:
                return

            # Get processed frame from navigation system
            frame = self.nav_system.get_display_frame(
                show_regions=self.show_regions_var.get(),
                show_stats=self.show_stats_var.get(),
                show_depth=self.show_depth_var.get()
            )

            if frame is not None:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Convert to PIL Image
                img = Image.fromarray(frame_rgb)

                # Resize to fit canvas (fill)
                canvas_width = self.video_canvas.winfo_width()
                canvas_height = self.video_canvas.winfo_height()

                if canvas_width > 1 and canvas_height > 1:
                    img = img.resize((canvas_width, canvas_height), Image.LANCZOS)

                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(image=img)

                # Update canvas image
                self.video_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                self.video_canvas.image = photo  # Keep reference

                # Update Overlays (Bring to front)
                self.video_canvas.tag_raise(self.overlay_status)
                self.video_canvas.tag_raise(self.overlay_fps)
                self.video_canvas.tag_raise(self.overlay_info)

                # Get latest stats
                stats = self.nav_system.get_system_status()
                
                # Update text
                status_text = "ACTIVE" if self.is_running else "PAUSED"
                self.video_canvas.itemconfig(self.overlay_status, text=f"Status: {status_text}", fill="green" if self.is_running else "red")
                
                fps = stats.get('fps', 0)
                self.video_canvas.itemconfig(self.overlay_fps, text=f"FPS: {fps:.1f}")
                
                info_text = f"Threshold: {self.threshold_var.get():.2f}"
                self.video_canvas.itemconfig(self.overlay_info, text=info_text, fill="purple")
                
        except Exception as e:
            print(f"Error in GUI update loop: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Schedule next update regardless of success/failure
            if self.is_running:
                self.update_job = self.root.after(config.UPDATE_INTERVAL_MS, self.update_video)

    def on_threshold_change(self, value):
        """Handle threshold slider change"""
        threshold = float(value)
        self.threshold_label.config(text=f"{threshold:.2f}")
        self.nav_system.set_threshold(threshold)

    def on_occupancy_change(self, value):
        """Handle occupancy slider change"""
        occupancy = float(value)
        self.occupancy_label.config(text=f"{occupancy:.1f}%")
        self.nav_system.set_min_occupancy(occupancy)

    def set_sensitivity(self, level):
        """Set sensitivity preset"""
        preset = config.SENSITIVITY_PRESETS.get(level)
        if preset:
            self.threshold_var.set(preset['threshold'])
            self.occupancy_var.set(preset['min_occupancy'])
            self.status_label.config(text=f"Sensitivity set to {level.upper()}")

    def on_closing(self):
        """Handle window close event"""
        if self.is_running:
            self.nav_system.stop()

        # Cleanup audio
        if self.nav_system.audio_feedback:
            self.nav_system.audio_feedback.shutdown()

        self.root.destroy()

    def run(self):
        """Start GUI main loop"""
        self.root.mainloop()