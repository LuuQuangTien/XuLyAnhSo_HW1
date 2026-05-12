import os
import tkinter as tk
from tkinter import ttk
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
        self.setup_buttons()

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

        tk.Button(self.left, text="Chọn thư mục", command=self.select_folder, bg="#48d141").pack(fill=tk.X)

        self.nav_container = tk.Frame(self.left)
        self.nav_container.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.tree_frame = tk.Frame(self.nav_container)
        self.tree = ttk.Treeview(self.tree_frame, show="tree")
        self.tree_scroll = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.thumb_frame = tk.Frame(self.nav_container)
        top_bar = tk.Frame(self.thumb_frame)
        top_bar.pack(fill=tk.X)
        tk.Button(top_bar, text="< Back", command=self.show_tree).pack(side=tk.LEFT)
        
        self.canvas = tk.Canvas(self.thumb_frame)
        self.thumb_scroll = ttk.Scrollbar(self.thumb_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.thumb_scroll.set)
        
        self.scroll_frame = tk.Frame(self.canvas)
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", width=250)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.thumb_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.show_tree()

        self.image_label = tk.Label(self.right, bg="gray")
        self.image_label.pack(pady=10)

        self.rgb_nav_frame = tk.Frame(self.right)
        self.rgb_title = tk.Label(self.rgb_nav_frame, font=("Arial", 16, "bold"))
        self.rgb_title.pack()

        nav = tk.Frame(self.rgb_nav_frame)
        nav.pack(fill=tk.X)

        tk.Button(nav, text="<<", command=self.rgb_prev).pack(side=tk.LEFT, padx=20)
        tk.Button(nav, text=">>", command=self.rgb_next).pack(side=tk.RIGHT, padx=20)

    def show_tree(self):
        self.thumb_frame.pack_forget()
        self.tree_frame.pack(fill=tk.BOTH, expand=True)

    def show_thumbs(self):
        self.tree_frame.pack_forget()
        self.thumb_frame.pack(fill=tk.BOTH, expand=True)

    def setup_buttons(self):
        pass

    def select_folder(self):
        path = filedialog.askdirectory()
        if not path:
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        root_node = self.tree.insert("", "end", text=os.path.basename(path), values=(path,))
        self.populate_tree(root_node, path)
        self.tree.item(root_node, open=True)
        self.show_tree()

    def populate_tree(self, parent, path):
        try:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    node = self.tree.insert(parent, "end", text=item, values=(full_path,))
                    self.populate_tree(node, full_path)
        except PermissionError:
            pass

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = selected[0]
        path = self.tree.item(item, "values")[0]
        
        images = self.logic.get_image_files(path)
        for w in self.scroll_frame.winfo_children():
            w.destroy()
        
        if not images:
            tk.Label(self.scroll_frame, text="No images").pack()
        else:
            for i, img in enumerate(images):
                thumb = self.logic.get_thumbnail(img)
                if not thumb:
                    continue

                btn = tk.Button(self.scroll_frame, image=thumb, command=lambda n=img: self.show_image(n))
                btn.image = thumb
                btn.grid(row=i // 3, column=i % 3)
                
        self.show_thumbs()

    def show_image(self, name):
        self.logic.load_image(name)
        img = self.logic.get_display_image(800, 600)

        if img:
            self.show_image_tk(img)

        self.hide_nav()

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