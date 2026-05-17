from tkinter import messagebox

import customtkinter as ctk
from .UIConfig import UIConfig

class SidebarUI:
    def setup_sidebar(self):
        self.tool_panel = ctk.CTkScrollableFrame(
            self.left,
            fg_color="transparent",
            corner_radius=0,
        )
        self.tool_panel.pack(fill="both", expand=True, padx=UIConfig.SMALL_PAD, pady=(2, UIConfig.MAIN_PAD))

        groups = [
            (
                "Basic Operations",
                [
                    ("Tach RGB", self.show_rgb),
                    ("Chuyen Gray", self.show_gray),
                    ("Rotate Demo", self.on_rotate),
                    ("Cat 1/4 anh", self.show_crop),
                ],
            ),
            (
                "Grayscale Transformation",
                [
                    ("Am anh", lambda: self.set_op("negative")),
                    ("Bien doi Logarit", lambda: self.set_op("log")),
                    ("Power-Law (Gamma)", lambda: self.set_op("gamma")),
                    ("Histogram Equalization", lambda: self.set_op("hist")),
                    ("Local Histogram", lambda: self.set_op("local_hist")),
                ],
            ),
            (
                "Lowpass Filtering (Spatial)",
                [
                    ("Loc Gaussian", lambda: self.set_op("gaussian")),
                    ("Loc Trung Binh", lambda: self.set_op("box")),
                    ("Loc Trung Vi", lambda: self.set_op("median")),
                ],
            ),
            (
                "Highpass Filtering (Spatial)",
                [
                    ("Laplace K1", lambda: self.set_op("laplacian_0")),
                    ("Laplace K2", lambda: self.set_op("laplacian_1")),
                    ("Laplace K3", lambda: self.set_op("laplacian_2")),
                    ("Laplace K4", lambda: self.set_op("laplacian_3")),
                    ("Loc Sobel", lambda: self.set_op("sobel")),
                    ("Loc Robert", lambda: self.set_op("robert")),
                    ("Loc Prewitt", lambda: self.set_op("prewitt")),
                ],
            ),
            (
                "Lowpass Filtering (Frequency)",
                [
                    ("Loc Ideal", lambda: self.set_op("freq_ideal_lowpass")),
                    ("Loc Butterworth", lambda: self.set_op("freq_butterworth_lowpass")),
                    ("Loc Gaussian", lambda: self.set_op("freq_gaussian_lowpass")),
                ],
            ),
            (
                "Highpass Filtering (Frequency)",
                [
                    ("Loc Ideal", lambda: self.set_op("freq_ideal_highpass")),
                    ("Loc Butterworth", lambda: self.set_op("freq_butterworth_highpass")),
                    ("Loc Gaussian", lambda: self.set_op("freq_gaussian_highpass")),
                ],
            ),
        ]

        for title, actions in groups:
            self._add_group(title, actions)

    def _add_group(self, title, actions):
        group = ctk.CTkFrame(
            self.tool_panel,
            fg_color="#ffffff",
            corner_radius=UIConfig.GROUP_CORNER,
            border_width=UIConfig.BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER_SOFT,
        )
        group.pack(fill="x", padx=4, pady=(0, 14))

        ctk.CTkLabel(
            group,
            text=title,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=UIConfig.COLOR_TEXT,
        ).pack(anchor="w", padx=UIConfig.MAIN_PAD, pady=(14, UIConfig.SMALL_PAD))

        for text, command in actions:
            ctk.CTkButton(
                group,
                text=text,
                command=command,
                height=UIConfig.BUTTON_HEIGHT,
                corner_radius=UIConfig.BUTTON_CORNER,
                fg_color=UIConfig.COLOR_BUTTON_SOFT,
                hover_color=UIConfig.COLOR_BUTTON_SOFT_HOVER,
                text_color=UIConfig.COLOR_TEXT_BLUE_DARK,
                anchor="w",
            ).pack(fill="x", padx=14, pady=(0, 10))

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
        if not self._ensure_image_selected():
            return

        self.current_op = op_name
        self.hide_nav()
        self.prepare_operation_panel(op_name)
        self.on_slide()
