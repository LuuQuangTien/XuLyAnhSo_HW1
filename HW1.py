import tkinter as tk
from tkinter import messagebox
from UI import UI
from Logic import HW1Logic

class HW1(UI):
    def __init__(self, root):
        self.degree = 0
        self.stop_rotate = True
        super().__init__(root)
        self.logic = HW1Logic()

    def setup_buttons(self):
        tk.Button(self.left, text="Tách RGB", command=self.show_rgb).pack(fill=tk.X, pady=5)
        tk.Button(self.left, text="Gray", command=self.show_gray).pack(fill=tk.X, pady=5)
        tk.Button(self.left, text="Rotate", command=self.on_rotate).pack(fill=tk.X, pady=5)
        tk.Button(self.left, text="Set 1/4", command=self.show_crop).pack(fill=tk.X, pady=5)

    def show_rgb(self):
        if self.logic.img_cv is None:
            messagebox.showwarning("Error", "Chọn ảnh trước")
            return

        self.rgb_imgs = self.logic.get_RGB_Layer(800, 600)
        self.rgb_page = 0

        self.rgb_nav_frame.pack(fill=tk.X, pady=10)
        self.update_rgb()

    def show_gray(self):
        if self.logic.img_cv is None:
            messagebox.showwarning("Error", "Chọn ảnh trước")
            return

        self.hide_nav()
        img = self.logic.get_Grayscale(800, 600)
        self.show_image_tk(img)

    def rotate_update(self):
        if self.stop_rotate or self.degree >= 750:
            return

        rotated = self.logic.get_Rotate_img(self.degree, self.scale)
        self.show_cv_image(rotated)

        self.degree += 15
        self.scale *= 0.9
        self.root.after(1000, self.rotate_update)

    def on_rotate(self):
        if self.logic.img_cv is None:
            messagebox.showwarning("Error", "Chọn ảnh trước")
            return

        self.hide_nav()
        self.degree = 0
        self.scale = 1.0
        self.stop_rotate = False

        def stop(e=None):
            self.stop_rotate = True
            img = self.logic.get_display_image(800, 600)
            self.show_image_tk(img)

        self.root.bind("<Escape>", stop)
        self.rotate_update()

    def show_crop(self):
        if self.logic.img_cv is None:
            messagebox.showwarning("Error", "Chọn ảnh trước")
            return

        self.hide_nav()
        cropped = self.logic.get_Crop_img()
        if cropped is not None:
            self.show_cv_image(cropped)
