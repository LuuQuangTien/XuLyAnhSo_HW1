import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk
from Logic import ImageLogic

class UI:
    def __init__(self, root):
        self.root = root
        self.logic = ImageLogic()

        self.degree = 0
        self.stop_rotate = True

        self.center(1200, 650)
        self.setup_UI()

    def center(self, w, h):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def hide_nav(self):
        self.rgb_nav_frame.pack_forget()

    def show_image_tk(self, tk_img):
        self.image_label.config(image=tk_img)
        self.image_label.image = tk_img

    def show_cv_image(self, cv_img):
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        pil.thumbnail((800, 600))
        tk_img = ImageTk.PhotoImage(pil)
        self.show_image_tk(tk_img)

    def setup_UI(self):
        self.left = tk.Frame(self.root, width=275)
        self.left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.left.pack_propagate(False)

        self.right = tk.Frame(self.root, bg="white")
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Button
        tk.Button(self.left, text="Chọn thư mục", command=self.select_folder, bg="#48d141").pack(fill=tk.X)

        # Scroll
        self.canvas = tk.Canvas(self.left)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.scroll_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        # Image
        self.image_label = tk.Label(self.right, bg="gray")
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # NAV RGB
        self.rgb_nav_frame = tk.Frame(self.right)
        self.rgb_title = tk.Label(self.rgb_nav_frame, font=("Arial", 16, "bold"))
        self.rgb_title.pack()

        nav = tk.Frame(self.rgb_nav_frame)
        nav.pack(fill=tk.X)

        tk.Button(nav, text="<<", command=self.rgb_prev).pack(side=tk.LEFT, padx=20)
        tk.Button(nav, text=">>", command=self.rgb_next).pack(side=tk.RIGHT, padx=20)

        # Actions
        tk.Button(self.left, text="Tách RGB", command=self.show_rgb).pack(fill=tk.X, pady=5)
        tk.Button(self.left, text="Gray", command=self.show_gray).pack(fill=tk.X, pady=5)
        tk.Button(self.left, text="Rotate", command=self.on_rotate).pack(fill=tk.X, pady=5)
        tk.Button(self.left, text="Crop 1/4", command=self.show_crop).pack(fill=tk.X, pady=5)

    def select_folder(self):
        path = filedialog.askdirectory()
        if not path:
            return

        images = self.logic.get_image_files(path)

        for w in self.scroll_frame.winfo_children():
            w.destroy()

        for i, img in enumerate(images):
            thumb = self.logic.get_thumbnail(img)
            if not thumb:
                continue

            btn = tk.Button(self.scroll_frame, image=thumb,
                            command=lambda n=img: self.show_image(n))
            btn.image = thumb
            btn.grid(row=i // 3, column=i % 3)

    def show_image(self, name):
        self.logic.load_image(name)
        img = self.logic.get_display_image(800, 600)

        if img:
            self.show_image_tk(img)

        self.hide_nav()

    def show_rgb(self):
        if self.logic.img_cv is None:
            messagebox.showwarning("Error", "Chọn ảnh trước")
            return

        self.rgb_imgs = self.logic.get_RGB_Layer(800, 600)
        self.rgb_page = 0

        self.rgb_nav_frame.pack(fill=tk.X, pady=10)
        self.update_rgb()

    def update_rgb(self):
        titles = ["Red Layer", "Green Layer", "Blue Layer"]
        colors = ["red", "green", "blue"]

        self.rgb_title.config(text=titles[self.rgb_page], fg=colors[self.rgb_page])
        self.show_image_tk(self.rgb_imgs[self.rgb_page])

    def rgb_prev(self):
        if self.rgb_page > 0:
            self.rgb_page -= 1
            self.update_rgb()

    def rgb_next(self):
        if self.rgb_page < 2:
            self.rgb_page += 1
            self.update_rgb()

    def show_gray(self):
        if self.logic.img_cv is None:
            messagebox.showwarning("Error", "Chọn ảnh trước")
            return

        self.hide_nav()
        img = self.logic.get_Grayscale(800, 600)
        self.show_image_tk(img)

    def rotate_update(self):
        if self.stop_rotate or self.degree >= 500:
            return

        rotated = self.logic.get_Rotate_img(self.degree)
        self.show_cv_image(rotated)

        self.degree += 5
        self.root.after(100, self.rotate_update)

    def on_rotate(self):
        if self.logic.img_cv is None:
            messagebox.showwarning("Error", "Chọn ảnh trước")
            return

        self.hide_nav()
        self.degree = 0
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