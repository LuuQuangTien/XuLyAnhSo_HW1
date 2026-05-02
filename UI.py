import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk
from Logic import ImageLogic

class UI:
    def __init__(self, root):
        self.root = root
        self.logic = ImageLogic()

        self.center(1200, 650)
        self.setup_UI()

    def center(self, w, h):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def setup_UI(self):
        self.left = tk.Frame(self.root, width=275)
        self.left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.left.pack_propagate(False)

        self.right = tk.Frame(self.root, bg="white")
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Button(self.left, text="Chọn thư mục", command=self.select_folder, background="#48d141").pack(fill=tk.X)

        self.canvas = tk.Canvas(self.left)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.scroll_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0,0), window=self.scroll_frame, anchor="nw")

        self.image_label = tk.Label(self.right, bg="gray")
        self.image_label.pack(fill=tk.BOTH, expand=True)

        self.rgb_nav_frame = tk.Frame(self.right)
        self.rgb_title = tk.Label(self.rgb_nav_frame, font=("Arial", 16, "bold"))
        self.rgb_title.pack(pady=5)
        nav_btns = tk.Frame(self.rgb_nav_frame)
        nav_btns.pack(fill=tk.X, pady=5)
        tk.Button(nav_btns, text="<<", command=self.rgb_prev).pack(side=tk.LEFT, padx=20)
        tk.Button(nav_btns, text=">>", command=self.rgb_next).pack(side=tk.RIGHT, padx=20)

        tk.Button(self.left, text="Tách RGB", command=self.show_rgb).pack(fill=tk.X, pady=5)
        tk.Button(self.left, text="Convert Gray", command=self.show_gray).pack(fill=tk.X, pady=5)
        tk.Button(self.left, text="Xoay hình ảnh", command=self.on_rotate).pack(fill=tk.X, pady=5)
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

            btn = tk.Button(self.scroll_frame, image=thumb, command=lambda n=img: self.show_image(n))
            btn.image = thumb
            btn.grid(row=i//3, column=i%3)

    def show_image(self, name):
        self.logic.load_image(name)
        img = self.logic.get_display_image(800, 600)

        if img:
            self.image_label.config(image=img)
            self.image_label.image = img
            
        if hasattr(self, 'rgb_nav_frame'):
            self.rgb_nav_frame.pack_forget()

    def show_rgb(self):
        if self.logic.img_cv is None:
            messagebox.showwarning("Error", "Chọn ảnh trước")
            return

        self.rgb_imgs = self.logic.get_RGB_Layer(800, 600)
        self.rgb_page = 0
        self.rgb_nav_frame.pack(fill=tk.X, pady=10)
        self.update_rgb_ui()

    def update_rgb_ui(self):
        titles = ["Red Layer", "Green Layer", "Blue Layer"]
        colors = ["red", "green", "blue"]
        self.rgb_title.config(text=titles[self.rgb_page], fg=colors[self.rgb_page])
        img = self.rgb_imgs[self.rgb_page]
        self.image_label.config(image=img)
        self.image_label.image = img

    def rgb_prev(self):
        if self.rgb_page > 0:
            self.rgb_page -= 1
            self.update_rgb_ui()

    def rgb_next(self):
        if self.rgb_page < 2:
            self.rgb_page += 1
            self.update_rgb_ui()

    def show_gray(self):
        if self.logic.img_cv is None:
            messagebox.showwarning("Error", "Chọn ảnh trước")
            return

        if hasattr(self, 'rgb_nav_frame'):
            self.rgb_nav_frame.pack_forget()
            
        img = self.logic.get_Grayscale(800, 600)
        self.image_label.config(image=img)
        self.image_label.image = img

    def rotate_update(self):
        if getattr(self, "stop_rotate", True):
            return

        rotated = self.logic.get_Rotate_img(self.degree)
        rgb = cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        pil.thumbnail((800, 600))

        tk_img = ImageTk.PhotoImage(pil)
        
        self.image_label.config(image=tk_img)
        self.image_label.image = tk_img
        self.degree += 5
        self.root.after(100, self.rotate_update)

    def on_rotate(self):
        if self.logic.img_cv is None:
            messagebox.showwarning("Error", "Chọn ảnh trước")
            return

        if hasattr(self, 'rgb_nav_frame'):
            self.rgb_nav_frame.pack_forget()

        self.degree = 0
        self.stop_rotate = False
        
        def stop_rotation(e=None):
            self.stop_rotate = True
            img = self.logic.get_display_image(800, 600)
            if img:
                self.image_label.config(image=img)
                self.image_label.image = img
            
        self.root.bind("<Escape>", stop_rotation)
        self.rotate_update()

    def show_crop(self):
        if self.logic.img_cv is None:
            messagebox.showwarning("Error", "Chọn ảnh trước")
            return

        if hasattr(self, 'rgb_nav_frame'):
            self.rgb_nav_frame.pack_forget()

        cropped = self.logic.get_Crop_img()
        if cropped is None:
            return

        rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        pil.thumbnail((800, 600))

        tk_img = ImageTk.PhotoImage(pil)
        self.image_label.config(image=tk_img)
        self.image_label.image = tk_img
