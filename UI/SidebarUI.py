from tkinter import messagebox, filedialog

import customtkinter as ctk

from .UIConfig import UIConfig

class SidebarUI:
    def setup_sidebar(self):
        self.hw_groups = {
            1: [
                (
                    "Quick Access",
                    [
                        ("Tach RGB", self.show_rgb),
                        ("Chuyen Gray", self.show_gray),
                        ("Rotate Demo", self.on_rotate),
                        ("Cat 1/4 anh", self.show_crop),
                    ],
                )
            ],
            2: [
                (
                    "Tone",
                    [
                        ("Am anh", lambda: self.set_op("negative")),
                        ("Bien doi Logarit", lambda: self.set_op("log")),
                        ("Power-Law (Gamma)", lambda: self.set_op("gamma")),
                        ("Histogram Equalization", lambda: self.set_op("hist")),
                        ("Local Histogram", lambda: self.set_op("local_hist")),
                    ],
                ),
                (
                    "Spatial Blur",
                    [
                        ("Loc Gaussian", lambda: self.set_op("gaussian")),
                        ("Loc Trung Binh", lambda: self.set_op("box")),
                        ("Loc Trung Vi", lambda: self.set_op("median")),
                    ],
                ),
                (
                    "Edge Detect",
                    [
                        ("Laplace K1", lambda: self.set_op("laplacian_0")),
                        ("Laplace K2", lambda: self.set_op("laplacian_1")),
                        ("Laplace K3", lambda: self.set_op("laplacian_2")),
                        ("Laplace K4", lambda: self.set_op("laplacian_3")),
                        ("Loc Sobel", lambda: self.set_op("sobel")),
                        ("Loc Robert", lambda: self.set_op("robert")),
                        ("Loc Prewitt", lambda: self.set_op("prewitt")),
                    ],
                )
            ],
            3: [
                (
                    "Freq Lowpass",
                    [
                        ("Loc Ideal", lambda: self.set_op("freq_ideal_lowpass")),
                        ("Loc Butterworth", lambda: self.set_op("freq_butterworth_lowpass")),
                        ("Loc Gaussian", lambda: self.set_op("freq_gaussian_lowpass")),
                    ],
                ),
                (
                    "Freq Highpass",
                    [
                        ("Loc Ideal", lambda: self.set_op("freq_ideal_highpass")),
                        ("Loc Butterworth", lambda: self.set_op("freq_butterworth_highpass")),
                        ("Loc Gaussian", lambda: self.set_op("freq_gaussian_highpass")),
                    ],
                )
            ],
            4: [
                (
                    "Morphology Basic",
                    [
                        ("Erosion", lambda: self.set_op("erosion")),
                        ("Dilation", lambda: self.set_op("dilation")),
                        ("Opening", lambda: self.set_op("opening")),
                        ("Closing", lambda: self.set_op("closing")),
                        ("Hit-or-Miss", lambda: self.set_op("hitmiss")),
                    ],
                ),
                (
                    "Morphology Advanced",
                    [
                        ("Boundary Extraction", lambda: self.set_op("boundary")),
                        ("Region Filling", lambda: self.set_op("region_fill")),
                        ("Connected Components", lambda: self.set_op("connected_comp")),
                        ("Convex Hull", lambda: self.set_op("convex_hull")),
                        ("Thinning", lambda: self.set_op("thinning")),
                        ("Thickening", lambda: self.set_op("thickening")),
                    ],
                )
            ],
            5: [
                (
                    "Video Segmentation",
                    [
                        ("Video / Camera Segment", lambda: self.set_op("video_segment")),
                    ],
                ),
                (
                    "Gaussian Threshold",
                    [
                        ("Optimal Threshold Plot", lambda: self.set_op("gaussian_threshold")),
                    ],
                ),
                (
                    "Segment & Count",
                    [
                        ("Segment Objects", lambda: self.set_op("segment_count")),
                    ],
                ),
            ]
        }

        self.select_hw(1)

    def select_hw(self, hw_num):
        self.active_hw = hw_num
        self._stop_video()  # Always stop video when switching HW tabs
        for idx, btn in self.hw_buttons.items():
            if idx == hw_num:
                btn.configure(
                    fg_color=UIConfig.COLOR_TOOL_ACTIVE,
                    hover_color=UIConfig.COLOR_PRIMARY_HOVER,
                    border_width=0,
                    text_color=UIConfig.COLOR_TEXT
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=UIConfig.COLOR_TOOL_HOVER,
                    border_width=1,
                    border_color=UIConfig.COLOR_BORDER,
                    text_color=UIConfig.COLOR_TEXT_ALT
                )

        self.current_op = None
        if hasattr(self, "slider_frame"):
            self.slider_frame.pack_forget()

        # Destroy old tool groups
        if hasattr(self, "tool_group_widgets"):
            for widget in self.tool_group_widgets:
                widget.destroy()
            self.tool_group_widgets.clear()

        groups = self.hw_groups.get(hw_num, [])
        if not groups:
            placeholder = ctk.CTkLabel(
                self.action_panel,
                text=f"HW{hw_num} has no tools assigned.",
                text_color=UIConfig.COLOR_TEXT_MUTED,
                font=ctk.CTkFont(size=UIConfig.FONT_BODY, slant="italic"),
            )
            placeholder.pack(pady=40)
            self.tool_group_widgets.append(placeholder)
            return

        for title, actions in groups:
            self._add_group_to_container(title, actions)

    def _add_group_to_container(self, title, actions):
        group = ctk.CTkFrame(
            self.action_panel,
            fg_color=UIConfig.COLOR_CARD_BG,
            corner_radius=UIConfig.GROUP_CORNER,
            border_width=UIConfig.BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER_SOFT,
        )
        group.pack(fill="x", padx=2, pady=(0, 10))
        self.tool_group_widgets.append(group)

        ctk.CTkLabel(
            group,
            text=title,
            font=ctk.CTkFont(size=UIConfig.FONT_GROUP, weight="bold"),
            text_color=UIConfig.COLOR_TEXT,
        ).pack(anchor="w", padx=UIConfig.INNER_PAD, pady=(8, 6))

        for text, command in actions:
            ctk.CTkButton(
                group,
                text=text,
                command=command,
                height=UIConfig.BUTTON_HEIGHT,
                corner_radius=UIConfig.BUTTON_CORNER,
                fg_color=UIConfig.COLOR_BUTTON_SOFT,
                hover_color=UIConfig.COLOR_BUTTON_SOFT_HOVER,
                text_color=UIConfig.COLOR_TEXT_ALT,
                anchor="w",
                font=ctk.CTkFont(size=UIConfig.FONT_BUTTON),
            ).pack(fill="x", padx=UIConfig.INNER_PAD, pady=(0, 6))

    def _ensure_image_selected(self):
        if self.logic.img_cv is None:
            messagebox.showwarning("Thieu anh", "Vui long chon anh truoc khi thuc hien thao tac.")
            return False
        return True

    def show_rgb(self):
        if not self._ensure_image_selected():
            return
        self.rgb_imgs = self.logic.get_RGB_Layer()
        self.rgb_page = 0
        self.rgb_nav_frame.pack(fill="x", padx=UIConfig.SECTION_PAD_X, pady=(0, UIConfig.SECTION_PAD_Y))
        self.update_rgb()

    def show_gray(self):
        if not self._ensure_image_selected():
            return
        self.hide_nav()
        gray_cv = self.logic.get_Grayscale()
        self.current_res_cv = gray_cv
        self.show_cv_image(gray_cv)

    def rotate_update(self):
        if self.stop_rotate or self.degree >= 750:
            return
        rotated = self.logic.get_Rotate_img(self.degree, self.scale)
        self.current_res_cv = rotated
        self.show_cv_image(rotated)
        self.degree += 15
        self.scale *= 0.9
        self.root.after(1000, self.rotate_update)

    def on_rotate(self):
        if not self._ensure_image_selected():
            return
        self.hide_nav()
        self.degree = 0
        self.scale = 1.0
        self.stop_rotate = False

        def stop(e=None):
            self.stop_rotate = True
            self.current_res_cv = None
            self.show_cv_image(self.logic.img_cv)

        self.root.bind("<Escape>", stop)
        self.rotate_update()

    def show_crop(self):
        if not self._ensure_image_selected():
            return
        self.hide_nav()
        cropped = self.logic.get_Crop_img()
        if cropped is not None:
            self.current_res_cv = cropped
            self.show_cv_image(cropped)

    def set_op(self, op_name):
        # Stop any running video when switching operations
        self._stop_video()

        # video_segment does not require a pre-loaded image
        if op_name != "video_segment" and not self._ensure_image_selected():
            return

        self.current_op = op_name
        self.hide_nav()
        self.prepare_operation_panel(op_name)

        # Don't call on_slide for video_segment (it manages its own display)
        if op_name != "video_segment":
            self.on_slide()

    # ──────────────────────────────────────────────
    # VIDEO PLAYBACK IN MAIN PREVIEW CANVAS
    # ──────────────────────────────────────────────

    def _init_video_state(self):
        """Ensure video state attributes exist."""
        if not hasattr(self, "_video_cap"):
            self._video_cap = None
        if not hasattr(self, "_video_subtractor"):
            self._video_subtractor = None
        if not hasattr(self, "_video_playing"):
            self._video_playing = False
        if not hasattr(self, "_video_prev_gray"):
            self._video_prev_gray = None
        if not hasattr(self, "_video_after_id"):
            self._video_after_id = None
        if not hasattr(self, "_video_method"):
            self._video_method = "MOG2"
        if not hasattr(self, "_video_zoom_set"):
            self._video_zoom_set = False

    def start_video(self):
        """Start video from file or camera based on current selector values."""
        import cv2
        self._init_video_state()
        self._stop_video()  # Clean up any existing session

        source = self.active_selectors.get("video_source")
        source_val = source.get() if source else "File"
        method_var = self.active_selectors.get("video_method")
        method = method_var.get() if method_var else "MOG2"
        self._video_method = method

        if source_val == "Camera":
            video_path = 0
        else:
            video_path = filedialog.askopenfilename(
                title="Select Video",
                filetypes=[
                    ("Video Files", "*.mp4 *.avi *.mkv *.mov *.wmv"),
                    ("All Files", "*.*"),
                ],
            )
            if not video_path:
                return

        success, cap, subtractor, total_frames = self.logic.video_segment_init(video_path, method)
        if not success:
            messagebox.showerror("Error", "Cannot open video / camera.")
            return

        self._video_cap = cap
        self._video_subtractor = subtractor
        self._video_playing = True
        self._video_prev_gray = None
        self._video_zoom_set = False

        src_label = "Camera" if source_val == "Camera" else "File"
        frames_str = f"{total_frames}" if total_frames > 0 else "live"
        self.image_title.configure(text=f"Video — {method} ({src_label})")
        self.image_meta.configure(text=f"Frames: {frames_str}")

        # Update button states
        if hasattr(self, "_video_start_btn") and self._video_start_btn.winfo_exists():
            self._video_start_btn.configure(state="disabled")
        if hasattr(self, "_video_stop_btn") and self._video_stop_btn.winfo_exists():
            self._video_stop_btn.configure(state="normal")

        self._video_frame_loop()

    def _stop_video(self):
        """Stop video playback and release resources."""
        self._init_video_state()

        if self._video_after_id is not None:
            self.root.after_cancel(self._video_after_id)
            self._video_after_id = None

        self._video_playing = False

        if self._video_cap is not None:
            self._video_cap.release()
            self._video_cap = None

        self._video_subtractor = None
        self._video_prev_gray = None
        self._video_zoom_set = False

        # Update button states (guard against destroyed widgets)
        if hasattr(self, "_video_start_btn") and self._video_start_btn.winfo_exists():
            self._video_start_btn.configure(state="normal")
        if hasattr(self, "_video_stop_btn") and self._video_stop_btn.winfo_exists():
            self._video_stop_btn.configure(state="disabled")

    def _toggle_video_pause(self):
        """Toggle pause/play for video."""
        self._init_video_state()
        if self._video_cap is None:
            return

        self._video_playing = not self._video_playing
        if hasattr(self, "_video_pause_btn") and self._video_pause_btn.winfo_exists():
            self._video_pause_btn.configure(
                text="▶ Play" if not self._video_playing else "⏸ Pause"
            )
        if self._video_playing:
            self._video_frame_loop()

    def _video_frame_loop(self):
        """Process and display next video frame in the main preview canvas."""
        self._init_video_state()

        if not self._video_playing or self._video_cap is None:
            return

        # Read toggle values
        show_bbox = True
        show_thresh = False
        if hasattr(self, "_video_bbox_var"):
            show_bbox = self._video_bbox_var.get()
        if hasattr(self, "_video_thresh_var"):
            show_thresh = self._video_thresh_var.get()

        ok, result, mask, gray = self.logic.video_segment_next_frame(
            self._video_cap, self._video_subtractor,
            self._video_method, self._video_prev_gray,
            show_bbox=show_bbox, show_thresh=show_thresh
        )

        if not ok:
            self._stop_video()
            self.image_meta.configure(text="Video ended")
            return

        self._video_prev_gray = gray

        # Display in main preview canvas
        pil_img = self.logic.cv_to_pil(result)
        if pil_img is not None:
            self.current_pil_image = pil_img.copy()
            self.current_res_cv = result
            if not self._video_zoom_set:
                self.reset_preview_zoom()
                self._video_zoom_set = True
            else:
                self.render_preview_image()

        # Schedule next frame (~30fps)
        self._video_after_id = self.root.after(33, self._video_frame_loop)
