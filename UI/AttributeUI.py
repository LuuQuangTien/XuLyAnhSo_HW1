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
        }

    def add_slider(self, key, label_text, from_val, to_val, default_val, is_int=False):
        frame = ctk.CTkFrame(self.slider_items, fg_color="transparent")
        frame.pack(fill="x", pady=6)

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(
            header,
            text=label_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#324559",
        ).pack(side="left")

        var = tk.DoubleVar(value=default_val)
        display_val = f"{int(default_val)}" if is_int else f"{default_val:.2f}"
        val_label = ctk.CTkLabel(
            header,
            text=display_val,
            width=UIConfig.VALUE_LABEL_WIDTH,
            text_color=UIConfig.COLOR_PRIMARY,
            font=ctk.CTkFont(size=13, weight="bold"),
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
            button_hover_color="#1e40af",
        )
        slider.pack(fill="x")
        self.active_sliders[key] = var

    def prepare_operation_panel(self, op_name):
        for widget in self.slider_items.winfo_children():
            widget.destroy()
        self.active_sliders.clear()

        title = self.operation_titles.get(op_name, op_name)
        self.slider_header.configure(text=title)
        self.slider_hint.configure(text="Thay doi thong so de xem truoc ket qua ngay tren vung preview.")
        self.action_title.configure(text=f"Tac vu: {title}")

        show_slider = True
        if op_name in ["negative", "hist", "sobel", "robert", "prewitt"] or op_name.startswith("laplacian_"):
            show_slider = False
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

        self.slider_frame.pack_forget()
        self.action_frame.pack_forget()

        if show_slider:
            self.slider_frame.pack(side="top", fill="x", padx=UIConfig.XSMALL_PAD, pady=(UIConfig.XSMALL_PAD, UIConfig.SMALL_PAD))
        self.action_frame.pack(side="top", fill="x", padx=UIConfig.XSMALL_PAD, pady=(0, UIConfig.INNER_PAD))

    def on_slide(self, *args):
        if self.current_op is None or self.logic.img_cv is None:
            return
        vals = {k: v.get() for k, v in self.active_sliders.items()}

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
