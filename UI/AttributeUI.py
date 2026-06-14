import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
from .UIConfig import UIConfig

class AttributeUI:
    def setup_action_panel(self):
        self.operation_titles = {
            "negative": "Am anh",
            "log": "Bien doi logarit",
            "gamma": "Power-law (Gamma)",
            "hist": "Histogram equalization",
            "local_hist": "Local histogram",
            "piecewise": "Piecewise linear",
            "gaussian": "Loc Gaussian",
            "box": "Loc trung binh",
            "median": "Loc trung vi",
            "laplacian_0": "Laplace K1",
            "laplacian_1": "Laplace K2",
            "laplacian_2": "Laplace K3",
            "laplacian_3": "Laplace K4",
            "sobel": "Loc Sobel",
            "robert": "Loc Robert",
            "prewitt": "Loc Prewitt",
            "freq_ideal_lowpass": "Ideal Lowpass",
            "freq_butterworth_lowpass": "Butterworth Lowpass",
            "freq_gaussian_lowpass": "Gaussian Lowpass",
            "freq_ideal_highpass": "Ideal Highpass",
            "freq_butterworth_highpass": "Butterworth Highpass",
            "freq_gaussian_highpass": "Gaussian Highpass",
            "erosion": "Erosion",
            "dilation": "Dilation",
            "opening": "Opening",
            "closing": "Closing",
            "hitmiss": "Hit-or-Miss",
            "boundary": "Boundary Extraction",
            "region_fill": "Region Filling",
            "connected_comp": "Connected Components",
            "convex_hull": "Convex Hull",
            "thinning": "Thinning",
            "thickening": "Thickening",
            "video_segment": "Video / Camera Segmentation",
            "gaussian_threshold": "Optimal Threshold (Gaussian)",
            "segment_count": "Segment & Count Objects",
            "face_recognition": "Face Recognition (Haar-like & PCA)",
        }

    def add_slider(self, key, label_text, from_val, to_val, default_val, is_int=False):
        frame = ctk.CTkFrame(self.slider_items, fg_color="transparent")
        frame.pack(fill="x", pady=4)

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 2))

        ctk.CTkLabel(
            header,
            text=label_text,
            font=ctk.CTkFont(size=UIConfig.FONT_BODY, weight="bold"),
            text_color=UIConfig.COLOR_TEXT_ALT,
        ).pack(side="left")

        var = tk.DoubleVar(value=default_val)
        display_val = f"{int(default_val)}" if is_int else f"{default_val:.2f}"
        val_label = ctk.CTkLabel(
            header,
            text=display_val,
            width=UIConfig.VALUE_LABEL_WIDTH,
            text_color=UIConfig.COLOR_TEXT_BLUE,
            font=ctk.CTkFont(size=UIConfig.FONT_BODY, weight="bold"),
        )
        val_label.pack(side="right")

        def _update_label(val):
            v = float(val)
            if is_int:
                v_int = int(round(v))
                if key in {"ksize", "kernel_size"} and v_int % 2 == 0:
                    v_int += 1
                var.set(v_int)
                val_label.configure(text=f"{v_int}")
            else:
                var.set(v)
                val_label.configure(text=f"{v:.2f}")
            self.on_slide()

        slider = ctk.CTkSlider(
            frame,
            variable=var,
            from_=from_val,
            to=to_val,
            command=_update_label,
            progress_color=UIConfig.COLOR_PRIMARY,
            button_color=UIConfig.COLOR_PRIMARY_HOVER,
            button_hover_color="#a9c7ff",
        )
        slider.pack(fill="x")
        self.active_sliders[key] = var

    def add_option_selector(self, key, label_text, options, default_val):
        frame = ctk.CTkFrame(self.slider_items, fg_color="transparent")
        frame.pack(fill="x", pady=4)

        ctk.CTkLabel(
            frame,
            text=label_text,
            font=ctk.CTkFont(size=UIConfig.FONT_BODY, weight="bold"),
            text_color=UIConfig.COLOR_TEXT_ALT,
        ).pack(anchor="w", pady=(0, 2))

        var = tk.StringVar(value=default_val)

        def _update_choice(choice):
            var.set(choice)
            if key == "custom_kernel_size" and self.current_op in ["erosion", "dilation", "opening", "closing"]:
                self.rebuild_morphology_controls(choice)
                return
            self.on_slide()

        selector = ctk.CTkSegmentedButton(
            frame,
            values=options,
            command=_update_choice,
            selected_color=UIConfig.COLOR_PRIMARY,
            selected_hover_color=UIConfig.COLOR_PRIMARY_HOVER,
            unselected_color=UIConfig.COLOR_BUTTON_SOFT,
            unselected_hover_color=UIConfig.COLOR_BUTTON_SOFT_HOVER,
            text_color=UIConfig.COLOR_TEXT,
            text_color_disabled=UIConfig.COLOR_TEXT_FAINT,
        )
        selector.pack(fill="x")
        selector.set(default_val)
        self.active_selectors[key] = var

    def add_kernel_matrix_editor(self, size=3):
        size = 5 if int(size) == 5 else 3

        wrapper = ctk.CTkFrame(self.slider_items, fg_color="transparent")
        wrapper.pack(fill="x", pady=6)

        ctk.CTkLabel(
            wrapper,
            text="Custom Kernel (chi dung khi chon custom)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=UIConfig.COLOR_TEXT_ALT,
        ).pack(anchor="w", pady=(0, 6))

        grid = ctk.CTkFrame(wrapper, fg_color="transparent")
        grid.pack(anchor="w")

        self.active_kernel_vars = []
        for row in range(size):
            row_vars = []
            for col in range(size):
                var = tk.StringVar(value="1")
                var.trace_add("write", lambda *args: self.on_slide())
                entry = ctk.CTkEntry(
                    grid,
                    width=44,
                    justify="center",
                    textvariable=var,
                    fg_color=UIConfig.COLOR_SUBTLE_BG,
                    border_color=UIConfig.COLOR_BORDER_SOFT,
                    text_color=UIConfig.COLOR_TEXT,
                )
                entry.grid(row=row, column=col, padx=3, pady=3)
                row_vars.append(var)
            self.active_kernel_vars.append(row_vars)

    def get_kernel_matrix_values(self):
        if not self.active_kernel_vars:
            return None

        matrix = []
        for row_vars in self.active_kernel_vars:
            row = []
            for var in row_vars:
                value = var.get().strip()
                try:
                    row.append(float(value))
                except ValueError:
                    row.append(1.0)
            matrix.append(row)
        return matrix

    def resize_kernel_matrix(self, matrix, new_size):
        new_size = 5 if int(new_size) == 5 else 3
        resized = [[1.0 for _ in range(new_size)] for _ in range(new_size)]
        if not matrix:
            return resized

        old_size = min(len(matrix), new_size)
        for row in range(old_size):
            old_row = matrix[row]
            for col in range(min(len(old_row), new_size)):
                resized[row][col] = old_row[col]
        return resized

    def populate_kernel_matrix(self, matrix):
        if not matrix or not self.active_kernel_vars:
            return

        for row_idx, row_vars in enumerate(self.active_kernel_vars):
            for col_idx, var in enumerate(row_vars):
                if row_idx < len(matrix) and col_idx < len(matrix[row_idx]):
                    value = matrix[row_idx][col_idx]
                    int_value = int(value)
                    var.set(str(int_value) if value == int_value else str(value))

    def add_morphology_controls(self, ksize=3, iterations=1, shape="rect", custom_kernel_size="3", kernel_matrix=None):
        self.add_slider("ksize", "Kernel Size", 1, 31, ksize, is_int=True)
        self.add_slider("iterations", "Iterations", 1, 10, iterations, is_int=True)
        self.add_option_selector("shape", "Structuring Element", ["rect", "ellipse", "cross", "custom"], shape)
        self.add_option_selector("custom_kernel_size", "Custom Kernel Size", ["3", "5"], custom_kernel_size)
        self.add_kernel_matrix_editor(size=custom_kernel_size)
        self.populate_kernel_matrix(self.resize_kernel_matrix(kernel_matrix, custom_kernel_size))

    def add_hitmiss_controls(self):
        """Add a 3x3 kernel editor for Hit-or-Miss with -1/0/1 values."""
        wrapper = ctk.CTkFrame(self.slider_items, fg_color="transparent")
        wrapper.pack(fill="x", pady=4)

        ctk.CTkLabel(
            wrapper,
            text="Kernel: 1=FG, 0=BG, -1=Don't care",
            font=ctk.CTkFont(size=UIConfig.FONT_BODY, weight="bold"),
            text_color=UIConfig.COLOR_TEXT_ALT,
        ).pack(anchor="w", pady=(0, 4))

        grid = ctk.CTkFrame(wrapper, fg_color="transparent")
        grid.pack(anchor="w")

        # Default: detect isolated foreground pixels
        defaults = [
            [-1, -1, -1],
            [-1,  1, -1],
            [-1, -1, -1],
        ]

        self.active_kernel_vars = []
        for row in range(3):
            row_vars = []
            for col in range(3):
                var = tk.StringVar(value=str(defaults[row][col]))
                var.trace_add("write", lambda *args: self.on_slide())
                entry = ctk.CTkEntry(
                    grid,
                    width=44,
                    justify="center",
                    textvariable=var,
                    fg_color=UIConfig.COLOR_SUBTLE_BG,
                    border_color=UIConfig.COLOR_BORDER_SOFT,
                    text_color=UIConfig.COLOR_TEXT,
                )
                entry.grid(row=row, column=col, padx=3, pady=3)
                row_vars.append(var)
            self.active_kernel_vars.append(row_vars)

    def rebuild_morphology_controls(self, custom_kernel_size):
        current_vals = {k: v.get() for k, v in self.active_sliders.items()}
        current_selectors = {k: v.get() for k, v in self.active_selectors.items()}
        current_matrix = self.get_kernel_matrix_values()

        for widget in self.slider_items.winfo_children():
            widget.destroy()
        self.active_sliders.clear()
        self.active_selectors.clear()
        self.active_kernel_vars = []

        self.add_morphology_controls(
            ksize=current_vals.get("ksize", 3),
            iterations=current_vals.get("iterations", 1),
            shape=current_selectors.get("shape", "rect"),
            custom_kernel_size=str(custom_kernel_size),
            kernel_matrix=current_matrix,
        )
        self.on_slide()
    def prepare_operation_panel(self, op_name):
        # Hide all active tool groups
        if hasattr(self, "tool_group_widgets"):
            for widget in self.tool_group_widgets:
                widget.pack_forget()

        for widget in self.slider_items.winfo_children():
            widget.destroy()
        self.active_sliders.clear()
        self.active_selectors.clear()
        self.active_kernel_vars = []

        title = self.operation_titles.get(op_name, op_name)
        self.slider_header.configure(text=title)
        
        # Configure Back button text to match the active Homework context
        if hasattr(self, "active_hw"):
            self.back_btn.configure(text=f"← Back to HW{self.active_hw} Tools")
        else:
            self.back_btn.configure(text="← Back to Tools")

        show_slider = True
        no_param_ops = ["negative", "hist", "sobel", "robert", "prewitt",
                        "region_fill", "connected_comp", "convex_hull", "thinning"]
        if op_name in no_param_ops or op_name.startswith("laplacian_"):
            show_slider = False

        if not show_slider:
            # High-fidelity placeholder for tools that require no parameters
            placeholder = ctk.CTkLabel(
                self.slider_items,
                text="No parameters needed for this tool.\nUse the action buttons on the leftmost sidebar\nto Apply or Reset changes.",
                text_color=UIConfig.COLOR_TEXT_MUTED,
                font=ctk.CTkFont(size=UIConfig.FONT_BODY, slant="italic"),
                justify="center",
            )
            placeholder.pack(pady=32, fill="x")
        elif op_name == "log":
            self.add_slider("c", "C Value", 1.0, 100.0, 40.0)
            self.add_slider("base", "Base", 1.01, 20.0, 2.71)
        elif op_name == "gamma":
            self.add_slider("c", "C Value", 0.1, 5.0, 1.0)
            self.add_slider("gamma", "Gamma Value", 0.1, 5.0, 1.0)
        elif op_name == "local_hist":
            self.add_slider("kernel_size", "Kernel Size", 3, 31, 7, is_int=True)
        elif op_name == "piecewise":
            self.add_slider("r1", "r1", 0, 255, 50, is_int=True)
            self.add_slider("s1", "s1", 0, 255, 20, is_int=True)
            self.add_slider("r2", "r2", 0, 255, 200, is_int=True)
            self.add_slider("s2", "s2", 0, 255, 230, is_int=True)
        elif op_name in ["box", "median"]:
            self.add_slider("ksize", "Kernel Size", 1, 31, 3, is_int=True)
        elif op_name == "gaussian":
            self.add_slider("ksize", "Kernel Size", 1, 31, 3, is_int=True)
            self.add_slider("sigma", "Sigma", 0.1, 10.0, 1.0)
        elif op_name in ["freq_ideal_lowpass", "freq_gaussian_lowpass", "freq_ideal_highpass", "freq_gaussian_highpass"]:
            self.add_slider("d0", "Cutoff D0", 1, 300, 30, is_int=True)
        elif op_name in ["freq_butterworth_lowpass", "freq_butterworth_highpass"]:
            self.add_slider("d0", "Cutoff D0", 1, 300, 30, is_int=True)
            self.add_slider("n", "Order n", 1, 10, 2, is_int=True)
        elif op_name in ["erosion", "dilation", "opening", "closing"]:
            self.add_morphology_controls()
        elif op_name == "hitmiss":
            self.add_hitmiss_controls()
        elif op_name == "boundary":
            self.add_morphology_controls()
        elif op_name == "thickening":
            self.add_slider("iterations", "Iterations", 1, 10, 3, is_int=True)
        elif op_name == "video_segment":
            import tkinter as tk
            # Source selector
            self.add_option_selector("video_source", "Source", ["File", "Camera"], "File")
            # Method selector
            self.add_option_selector("video_method", "Method", ["MOG2", "KNN", "Frame Diff"], "MOG2")

            # Buttons: Start / Pause / Stop
            btn_frame = ctk.CTkFrame(self.slider_items, fg_color="transparent")
            btn_frame.pack(fill="x", pady=6)

            self._video_start_btn = ctk.CTkButton(
                btn_frame, text="▶ Start", command=self.start_video,
                height=UIConfig.BUTTON_HEIGHT, corner_radius=UIConfig.BUTTON_CORNER,
                fg_color=UIConfig.COLOR_SUCCESS, hover_color=UIConfig.COLOR_SUCCESS_HOVER,
                text_color=UIConfig.COLOR_TEXT,
                font=ctk.CTkFont(size=UIConfig.FONT_BUTTON, weight="bold"),
            )
            self._video_start_btn.pack(side="left", fill="x", expand=True, padx=(0, 3))

            self._video_pause_btn = ctk.CTkButton(
                btn_frame, text="⏸ Pause", command=self._toggle_video_pause,
                height=UIConfig.BUTTON_HEIGHT, corner_radius=UIConfig.BUTTON_CORNER,
                fg_color=UIConfig.COLOR_PRIMARY, hover_color=UIConfig.COLOR_PRIMARY_HOVER,
                text_color=UIConfig.COLOR_TEXT,
                font=ctk.CTkFont(size=UIConfig.FONT_BUTTON, weight="bold"),
            )
            self._video_pause_btn.pack(side="left", fill="x", expand=True, padx=(0, 3))

            self._video_stop_btn = ctk.CTkButton(
                btn_frame, text="⏹ Stop", command=self._stop_video, state="disabled",
                height=UIConfig.BUTTON_HEIGHT, corner_radius=UIConfig.BUTTON_CORNER,
                fg_color=UIConfig.COLOR_DANGER, hover_color="#ff7777",
                text_color=UIConfig.COLOR_TEXT,
                font=ctk.CTkFont(size=UIConfig.FONT_BUTTON, weight="bold"),
            )
            self._video_stop_btn.pack(side="left", fill="x", expand=True)

            # Toggle switches
            toggle_frame = ctk.CTkFrame(self.slider_items, fg_color="transparent")
            toggle_frame.pack(fill="x", pady=6)

            self._video_bbox_var = tk.BooleanVar(value=True)
            ctk.CTkSwitch(
                toggle_frame, text="Bounding Box",
                variable=self._video_bbox_var,
                onvalue=True, offvalue=False,
                progress_color=UIConfig.COLOR_SUCCESS,
                text_color=UIConfig.COLOR_TEXT_ALT,
                font=ctk.CTkFont(size=UIConfig.FONT_BODY),
            ).pack(anchor="w", pady=2)

            self._video_thresh_var = tk.BooleanVar(value=False)
            ctk.CTkSwitch(
                toggle_frame, text="Threshold View",
                variable=self._video_thresh_var,
                onvalue=True, offvalue=False,
                progress_color=UIConfig.COLOR_PRIMARY,
                text_color=UIConfig.COLOR_TEXT_ALT,
                font=ctk.CTkFont(size=UIConfig.FONT_BODY),
            ).pack(anchor="w", pady=2)
        elif op_name == "gaussian_threshold":
            self.add_slider("mu1", "μ₁ (Background Mean)", 0, 255, 80, is_int=True)
            self.add_slider("mu2", "μ₂ (Object Mean)", 0, 255, 180, is_int=True)
            self.add_slider("sigma", "σ (Std Deviation)", 1, 80, 20, is_int=True)
            self.add_slider("p_percent", "p% (Object Proportion)", 1, 99, 50, is_int=True)
        elif op_name == "segment_count":
            self.add_slider("angle", "Light Angle (°)", 0, 360, 0, is_int=True)
            self.add_slider("intensity", "Light Intensity", 0.0, 1.0, 0.0)
            self.add_slider("min_area", "Min Object Area", 10, 5000, 100, is_int=True)
        elif op_name == "face_recognition":
            # Informational Label
            info_frame = ctk.CTkFrame(self.slider_items, fg_color=UIConfig.COLOR_SUBTLE_BG, corner_radius=UIConfig.CARD_CORNER)
            info_frame.pack(fill="x", pady=6, padx=2)
            
            info_label = ctk.CTkLabel(
                info_frame,
                text="Face Detection (Haar Cascade)\n\nThis tool uses Haar-like features and a cascade classifier to detect faces in real-time on your webcam feed.",
                font=ctk.CTkFont(size=UIConfig.FONT_BODY),
                text_color=UIConfig.COLOR_TEXT_ALT,
                justify="left",
                wraplength=250
            )
            info_label.pack(fill="x", padx=10, pady=12)
            
            # Status Label
            self._face_status_label = ctk.CTkLabel(
                self.slider_items,
                text="Status: Idle",
                font=ctk.CTkFont(size=UIConfig.FONT_BODY, weight="bold"),
                text_color=UIConfig.COLOR_TEXT_MUTED
            )
            self._face_status_label.pack(anchor="w", pady=4, padx=2)
            
            # Separator
            ctk.CTkFrame(self.slider_items, height=1, fg_color=UIConfig.COLOR_BORDER).pack(fill="x", pady=6)
            
            # Webcam action frame (Start / Stop)
            action_frame = ctk.CTkFrame(self.slider_items, fg_color="transparent")
            action_frame.pack(fill="x", pady=6)
            
            self._btn_start_recon = ctk.CTkButton(
                action_frame,
                text="▶ Start Camera",
                command=self.start_face_detection,
                height=UIConfig.BUTTON_HEIGHT,
                corner_radius=UIConfig.BUTTON_CORNER,
                fg_color=UIConfig.COLOR_SUCCESS,
                hover_color=UIConfig.COLOR_SUCCESS_HOVER,
                text_color=UIConfig.COLOR_TEXT,
                font=ctk.CTkFont(size=UIConfig.FONT_BUTTON, weight="bold")
            )
            self._btn_start_recon.pack(side="left", fill="x", expand=True, padx=(0, 3))
            
            self._btn_stop_recon = ctk.CTkButton(
                action_frame,
                text="⏹ Stop Camera",
                command=self._stop_video,
                height=UIConfig.BUTTON_HEIGHT,
                corner_radius=UIConfig.BUTTON_CORNER,
                fg_color=UIConfig.COLOR_DANGER,
                hover_color="#ff7777",
                text_color=UIConfig.COLOR_TEXT,
                font=ctk.CTkFont(size=UIConfig.FONT_BUTTON, weight="bold")
            )
            self._btn_stop_recon.pack(side="left", fill="x", expand=True)

        # Always pack the slider frame to show the back button and active tool header
        self.slider_frame.pack(fill="both", expand=True)

    def on_slide(self, *args):
        if self.current_op is None or self.logic.img_cv is None:
            return
        vals = {k: v.get() for k, v in self.active_sliders.items()}
        vals.update({k: v.get() for k, v in self.active_selectors.items()})

        custom_kernel_size = 5 if vals.get("custom_kernel_size") == "5" else 3

        res_cv = None
        if self.current_op == "negative":
            res_cv = self.logic.negative_transformation()
        elif self.current_op == "log":
            res_cv = self.logic.log_transformation(c=vals.get("c", 40.0), base=vals.get("base", 2.71))
        elif self.current_op == "gamma":
            res_cv = self.logic.powerLaw_transformation(c=vals.get("c", 1.0), gamma=vals.get("gamma", 1.0))
        elif self.current_op == "hist":
            res_cv = self.logic.histogram_equalization()
        elif self.current_op == "local_hist":
            res_cv = self.logic.apply_local_hist(kernel_size=vals.get("kernel_size", 7))
        elif self.current_op == "piecewise":
            res_cv = self.logic.piecewise_linear_transformation(
                r1=vals.get("r1", 50),
                s1=vals.get("s1", 20),
                r2=vals.get("r2", 200),
                s2=vals.get("s2", 230),
            )
        elif self.current_op == "gaussian":
            res_cv = self.logic.gaussian_frequency_filter(ksize=vals.get("ksize", 3), sigma=vals.get("sigma", 1.0))
        elif self.current_op == "box":
            res_cv = self.logic.box_filter(ksize=vals.get("ksize", 3))
        elif self.current_op == "median":
            res_cv = self.logic.median_filter(ksize=vals.get("ksize", 3))
        elif self.current_op.startswith("laplacian_"):
            idx = int(self.current_op.split("_")[1])
            res_cv = self.logic.laplacian_filter(kernel_idx=idx)
        elif self.current_op == "sobel":
            res_cv = self.logic.sobel_filter()
        elif self.current_op == "robert":
            res_cv = self.logic.robert_filter()
        elif self.current_op == "prewitt":
            res_cv = self.logic.prewitt_filter()
        elif self.current_op == "freq_ideal_lowpass":
            res_cv = self.logic.ideal_frequency_filter(D0=vals.get("d0", 30), highpass=False)
        elif self.current_op == "freq_butterworth_lowpass":
            res_cv = self.logic.butterworth_frequency_filter(D0=vals.get("d0", 30), n=vals.get("n", 2), highpass=False, )
        elif self.current_op == "freq_gaussian_lowpass":
            res_cv = self.logic.gaussian_frequency_filter(D0=vals.get("d0", 30), highpass=False)
        elif self.current_op == "freq_ideal_highpass":
            res_cv = self.logic.ideal_frequency_filter(D0=vals.get("d0", 30), highpass=True)
        elif self.current_op == "freq_butterworth_highpass":
            res_cv = self.logic.butterworth_frequency_filter(D0=vals.get("d0", 30), n=vals.get("n", 2), highpass=True, )
        elif self.current_op == "freq_gaussian_highpass":
            res_cv = self.logic.gaussian_frequency_filter(D0=vals.get("d0", 30), highpass=True)
        elif self.current_op == "erosion":
            res_cv = self.logic.erosion(
                ksize=custom_kernel_size if vals.get("shape") == "custom" else vals.get("ksize", 3),
                shape=vals.get("shape", "rect"),
                iterations=vals.get("iterations", 1),
                kernel_matrix=self.get_kernel_matrix_values(),
            )
        elif self.current_op == "dilation":
            res_cv = self.logic.dilation(
                ksize=custom_kernel_size if vals.get("shape") == "custom" else vals.get("ksize", 3),
                shape=vals.get("shape", "rect"),
                iterations=vals.get("iterations", 1),
                kernel_matrix=self.get_kernel_matrix_values(),
            )
        elif self.current_op == "opening":
            res_cv = self.logic.opening(
                ksize=custom_kernel_size if vals.get("shape") == "custom" else vals.get("ksize", 3),
                shape=vals.get("shape", "rect"),
                iterations=vals.get("iterations", 1),
                kernel_matrix=self.get_kernel_matrix_values(),
            )
        elif self.current_op == "closing":
            res_cv = self.logic.closing(
                ksize=custom_kernel_size if vals.get("shape") == "custom" else vals.get("ksize", 3),
                shape=vals.get("shape", "rect"),
                iterations=vals.get("iterations", 1),
                kernel_matrix=self.get_kernel_matrix_values(),
            )
        elif self.current_op == "hitmiss":
            res_cv = self.logic.hitmiss(kernel_matrix=self.get_kernel_matrix_values())
        elif self.current_op == "boundary":
            res_cv = self.logic.boundary_extraction(
                ksize=custom_kernel_size if vals.get("shape") == "custom" else vals.get("ksize", 3),
                shape=vals.get("shape", "rect"),
                kernel_matrix=self.get_kernel_matrix_values(),
            )
        elif self.current_op == "region_fill":
            res_cv = self.logic.region_filling()
        elif self.current_op == "connected_comp":
            res_cv = self.logic.connected_components()
        elif self.current_op == "convex_hull":
            res_cv = self.logic.convex_hull()
        elif self.current_op == "thinning":
            res_cv = self.logic.thinning()
        elif self.current_op == "thickening":
            res_cv = self.logic.thickening(iterations=vals.get("iterations", 3))
        elif self.current_op == "gaussian_threshold":
            mu1 = vals.get("mu1", 80)
            mu2 = vals.get("mu2", 180)
            sigma = vals.get("sigma", 20)
            p = vals.get("p_percent", 50) / 100.0
            res_cv, threshold = self.logic.plot_gaussian_threshold(mu1, mu2, sigma, p)
            if res_cv is not None:
                self.current_res_cv = res_cv
                self.show_cv_image(res_cv)
                self.image_meta.configure(text=f"T = {threshold:.2f}")
            return
        elif self.current_op == "segment_count":
            angle = int(vals.get("angle", 0))
            intensity = vals.get("intensity", 0.0)
            min_area = int(vals.get("min_area", 100))
            annotated, count, T, mu1, mu2, sigma, p = self.logic.segment_count_objects(
                angle_deg=angle, intensity=intensity, min_area=min_area
            )
            if annotated is not None:
                self.current_res_cv = annotated
                self.show_cv_image(annotated)
                self.image_meta.configure(
                    text=f"Objects: {count} | T={T:.1f} | μ₁={mu1:.0f} μ₂={mu2:.0f} | σ={sigma:.0f} | p={p:.0%}"
                )
            return

        if res_cv is not None:
            self.current_res_cv = res_cv
            self.show_cv_image(res_cv)

    def reset_img(self):
        if self.logic.img_cv is None:
            return
        self.current_res_cv = None
        self.show_cv_image(self.logic.img_cv)

    def apply_changes(self):
        if self.current_res_cv is not None:
            success = self.logic.apply_current_image(self.current_res_cv)
            if not success:
                messagebox.showerror("Loi", "Khong the cap nhat file anh goc.")
                return
            self.current_res_cv = self.logic.img_cv.copy()
            self.show_cv_image(self.logic.img_cv)
            if hasattr(self, "refresh_thumbnail") and self.logic.current_image_name is not None:
                self.refresh_thumbnail(self.logic.current_image_name)
            self.slider_frame.pack_forget()
            self.show_action_bar()
            self.current_op = None

    def download_image(self):
        if self.current_res_cv is None:
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg"), ("All Files", "*.*")],
        )
        if path:
            success = self.logic.save_image(path, self.current_res_cv)
            if success:
                messagebox.showinfo("Thanh cong", f"Da luu anh tai:\n{path}")
            else:
                messagebox.showerror("Loi", "Khong the luu anh.")
