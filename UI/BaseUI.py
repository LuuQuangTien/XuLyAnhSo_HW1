import os
import tkinter as tk
from tkinter import filedialog, ttk

import customtkinter as ctk
from PIL import Image, ImageTk

from .UIConfig import UIConfig

class BaseUI:
    def __init__(self, root):
        self.root = root
        self.logic = None
        self.thumb_buttons = []
        self.thumb_images = {}
        self.selected_thumb_name = None
        self.current_img = None
        self.current_pil_image = None
        self.preview_image_id = None
        self.preview_text_id = None
        self.preview_zoom = 1.0
        self.preview_min_zoom = 0.1
        self.preview_max_zoom = 8.0
        self.col_count = UIConfig.COL_COUNT

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.root.configure(fg_color=UIConfig.COLOR_APP_BG)
        self.root.minsize(UIConfig.WINDOW_MIN_WIDTH, UIConfig.WINDOW_MIN_HEIGHT)
        self.root.after(0, self.maximize_window)

    def maximize_window(self):
        self.root.update_idletasks()
        self.root.state("zoomed")

    def setup_base_layout(self):
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=UIConfig.MAIN_PAD, pady=UIConfig.MAIN_PAD)

        self.left = ctk.CTkFrame(
            self.main_frame,
            width=UIConfig.LEFT_PANEL_WIDTH,
            corner_radius=UIConfig.PANEL_CORNER,
            fg_color=UIConfig.COLOR_LEFT_BG,
            border_width=UIConfig.BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
        )
        self.left.pack(side="left", fill="y")
        self.left.pack_propagate(False)

        self.right = ctk.CTkFrame(
            self.main_frame,
            corner_radius=UIConfig.OUTER_CORNER,
            fg_color=UIConfig.COLOR_RIGHT_BG,
        )
        self.right.pack(side="left", fill="both", expand=True, padx=(UIConfig.MAIN_PAD, 0))

        self.build_sidebar_shell()
        self.build_preview_shell()
        self.build_action_shell()

    def build_sidebar_shell(self):
        self.select_btn = ctk.CTkButton(
            self.left,
            text="Chon thu muc anh",
            command=self.select_folder,
            height=UIConfig.PRIMARY_BUTTON_HEIGHT,
            corner_radius=UIConfig.SMALL_CORNER,
            fg_color=UIConfig.COLOR_PRIMARY,
            hover_color=UIConfig.COLOR_PRIMARY_HOVER,
            font=ctk.CTkFont(size=UIConfig.FONT_BUTTON, weight="bold"),
        )
        self.select_btn.pack(fill="x", padx=UIConfig.MAIN_PAD, pady=(UIConfig.MAIN_PAD, 14))

        self.nav_container = ctk.CTkFrame(
            self.left,
            height=UIConfig.NAV_PANEL_HEIGHT,
            corner_radius=UIConfig.GROUP_CORNER,
            fg_color=UIConfig.COLOR_CARD_BG,
            border_width=UIConfig.BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
        )
        self.nav_container.pack(fill="x", expand=False, padx=UIConfig.MAIN_PAD, pady=(0, UIConfig.SMALL_PAD))
        self.nav_container.pack_propagate(False)

        self.tree_frame = ctk.CTkFrame(self.nav_container, fg_color="transparent")
        self._build_tree_view()

        self.thumb_frame = ctk.CTkFrame(self.nav_container, fg_color="transparent")
        self._build_thumbnail_view()

        self.show_tree()

    def _build_tree_view(self):
        ctk.CTkLabel(
            self.tree_frame,
            text="Thu muc anh",
            font=ctk.CTkFont(size=UIConfig.FONT_GROUP, weight="bold"),
            text_color=UIConfig.COLOR_TEXT,
        ).pack(anchor="w", padx=14, pady=(14, UIConfig.XSMALL_PAD))

        tree_wrap = ctk.CTkFrame(
            self.tree_frame,
            fg_color=UIConfig.COLOR_CARD_BG,
            corner_radius=UIConfig.SMALL_CORNER,
        )
        tree_wrap.pack(fill="both", expand=True, padx=UIConfig.SMALL_PAD, pady=(0, UIConfig.SMALL_PAD))

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Custom.Treeview",
            background=UIConfig.COLOR_CARD_BG,
            fieldbackground=UIConfig.COLOR_CARD_BG,
            foreground="#1f2937",
            rowheight=UIConfig.TREE_ROW_HEIGHT,
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 10),
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", "#dbeafe")],
            foreground=[("selected", "#2563eb")],
        )

        self.tree = ttk.Treeview(tree_wrap, show="tree", style="Custom.Treeview", selectmode="browse")
        self.tree_scroll = ttk.Scrollbar(tree_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(UIConfig.XSMALL_PAD, 0), pady=UIConfig.XSMALL_PAD)
        self.tree_scroll.pack(side="right", fill="y", padx=(0, UIConfig.XSMALL_PAD), pady=UIConfig.XSMALL_PAD)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def _build_thumbnail_view(self):
        top_bar = ctk.CTkFrame(self.thumb_frame, fg_color="transparent")
        top_bar.pack(fill="x", padx=UIConfig.SMALL_PAD, pady=(UIConfig.SMALL_PAD, UIConfig.XSMALL_PAD))

        ctk.CTkButton(
            top_bar,
            text="Back",
            width=100,
            height=UIConfig.SMALL_BUTTON_HEIGHT,
            command=self.show_tree,
            corner_radius=UIConfig.XS_CORNER,
            fg_color=UIConfig.COLOR_SECONDARY_SOFT,
            hover_color=UIConfig.COLOR_SECONDARY_SOFT_HOVER,
            text_color=UIConfig.COLOR_TEXT_BLUE_DARK,
        ).pack(side="left")

        self.thumb_title = ctk.CTkLabel(
            top_bar,
            text="Danh sach anh",
            font=ctk.CTkFont(size=UIConfig.FONT_GROUP, weight="bold"),
            text_color=UIConfig.COLOR_TEXT,
        )
        self.thumb_title.pack(side="left", padx=UIConfig.SMALL_PAD)

        self.thumb_scroll_frame = ctk.CTkScrollableFrame(
            self.thumb_frame,
            corner_radius=UIConfig.SMALL_CORNER,
            fg_color=UIConfig.COLOR_SUBTLE_BG,
        )
        self.thumb_scroll_frame.pack(fill="both", expand=True, padx=UIConfig.SMALL_PAD, pady=(0, UIConfig.SMALL_PAD))

        for col in range(self.col_count):
            self.thumb_scroll_frame.grid_columnconfigure(col, weight=1)

    def build_preview_shell(self):
        self.preview_header = ctk.CTkFrame(self.right, fg_color="transparent")
        self.preview_header.pack(fill="x", padx=UIConfig.SECTION_PAD_X, pady=(22, 14))

        ctk.CTkLabel(
            self.preview_header,
            text="Preview",
            font=ctk.CTkFont(size=UIConfig.FONT_TITLE, weight="bold"),
            text_color="#1c2a39",
        ).pack(anchor="w")

        self.preview_panel = ctk.CTkFrame(self.right, fg_color="transparent")
        self.preview_panel.pack(fill="both", expand=True, padx=UIConfig.SECTION_PAD_X, pady=(0, UIConfig.SMALL_PAD))

        self.image_card = ctk.CTkFrame(
            self.preview_panel,
            corner_radius=UIConfig.OUTER_CORNER,
            fg_color=UIConfig.COLOR_CARD_BG,
            border_width=UIConfig.BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
        )
        self.image_card.pack(fill="both", expand=True)

        self.image_info_bar = ctk.CTkFrame(self.image_card, fg_color="transparent")
        self.image_info_bar.pack(fill="x", padx=UIConfig.INNER_PAD, pady=(UIConfig.INNER_PAD, 10))

        self.image_title = ctk.CTkLabel(
            self.image_info_bar,
            text="Chua chon anh",
            font=ctk.CTkFont(size=UIConfig.FONT_SECTION, weight="bold"),
            text_color=UIConfig.COLOR_TEXT,
        )
        self.image_title.pack(anchor="w")

        self.image_stage = ctk.CTkFrame(
            self.image_card,
            corner_radius=UIConfig.CARD_CORNER,
            fg_color=UIConfig.COLOR_STAGE_BG,
        )
        self.image_stage.pack(fill="both", expand=True, padx=UIConfig.INNER_PAD, pady=(0, UIConfig.INNER_PAD))
        self.image_stage.grid_rowconfigure(0, weight=1)
        self.image_stage.grid_columnconfigure(0, weight=1)

        self.preview_canvas = tk.Canvas(
            self.image_stage,
            bg=UIConfig.COLOR_STAGE_BG,
            bd=0,
            highlightthickness=0,
        )
        self.preview_h_scroll = ttk.Scrollbar(self.image_stage, orient="horizontal", command=self.preview_canvas.xview)
        self.preview_v_scroll = ttk.Scrollbar(self.image_stage, orient="vertical", command=self.preview_canvas.yview)
        self.preview_canvas.configure(
            xscrollcommand=self.preview_h_scroll.set,
            yscrollcommand=self.preview_v_scroll.set,
        )
        self.preview_canvas.grid(row=0, column=0, sticky="nsew")
        self.preview_v_scroll.grid(row=0, column=1, sticky="ns")
        self.preview_h_scroll.grid(row=1, column=0, sticky="ew")

        self.preview_text_id = self.preview_canvas.create_text(
            0,
            0,
            text="Khu vuc xem anh",
            fill=UIConfig.COLOR_TEXT_FAINT,
            font=("Segoe UI", 22, "bold"),
            anchor="center",
        )

        self.preview_canvas.bind("<Configure>", self.on_preview_canvas_configure)
        self.preview_canvas.bind("<MouseWheel>", self.on_preview_mousewheel)
        self.preview_canvas.bind("<Shift-MouseWheel>", self.on_preview_shift_mousewheel)
        self.preview_canvas.bind("<Control-MouseWheel>", self.on_preview_zoom)

        self.rgb_nav_frame = ctk.CTkFrame(
            self.preview_panel,
            fg_color=UIConfig.COLOR_ACCENT_BG,
            corner_radius=UIConfig.GROUP_CORNER,
        )
        self.rgb_title = ctk.CTkLabel(
            self.rgb_nav_frame,
            text="",
            font=ctk.CTkFont(size=UIConfig.FONT_GROUP, weight="bold"),
        )
        self.rgb_title.pack(pady=(UIConfig.SMALL_PAD, 6))

        nav = ctk.CTkFrame(self.rgb_nav_frame, fg_color="transparent")
        nav.pack(fill="x", padx=14, pady=(0, UIConfig.SMALL_PAD))

        ctk.CTkButton(
            nav,
            text="Truoc",
            command=self.rgb_prev,
            height=UIConfig.SMALL_BUTTON_HEIGHT,
            corner_radius=UIConfig.XS_CORNER,
            fg_color=UIConfig.COLOR_PRIMARY_SOFT,
            hover_color=UIConfig.COLOR_PRIMARY_SOFT_HOVER,
            text_color=UIConfig.COLOR_TEXT_BLUE,
        ).pack(side="left", fill="x", expand=True, padx=(0, UIConfig.XSMALL_PAD))

        ctk.CTkButton(
            nav,
            text="Sau",
            command=self.rgb_next,
            height=UIConfig.SMALL_BUTTON_HEIGHT,
            corner_radius=UIConfig.XS_CORNER,
            fg_color=UIConfig.COLOR_PRIMARY_SOFT,
            hover_color=UIConfig.COLOR_PRIMARY_SOFT_HOVER,
            text_color=UIConfig.COLOR_TEXT_BLUE,
        ).pack(side="left", fill="x", expand=True)

    def build_action_shell(self):
        self.action_panel = ctk.CTkScrollableFrame(
            self.right,
            corner_radius=UIConfig.OUTER_CORNER,
            fg_color=UIConfig.COLOR_SUBTLE_BG,
            border_width=UIConfig.BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
        )
        self.action_panel.pack(fill="x", expand=False, padx=UIConfig.SECTION_PAD_X, pady=(0, UIConfig.SECTION_PAD_Y))

        self.slider_frame = ctk.CTkFrame(
            self.action_panel,
            corner_radius=UIConfig.CARD_CORNER,
            fg_color=UIConfig.COLOR_CARD_BG,
            border_width=UIConfig.BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
        )
        self.slider_header = ctk.CTkLabel(
            self.slider_frame,
            text="Dieu chinh tham so",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=UIConfig.COLOR_TEXT,
        )
        self.slider_header.pack(anchor="w", padx=UIConfig.INNER_PAD, pady=(UIConfig.MAIN_PAD, 6))

        self.slider_hint = ctk.CTkLabel(
            self.slider_frame,
            text="Thay doi thong so de xem ket qua ngay lap tuc.",
            font=ctk.CTkFont(size=12),
            text_color="#748397",
        )
        self.slider_hint.pack(anchor="w", padx=UIConfig.INNER_PAD, pady=(0, UIConfig.XSMALL_PAD))

        self.slider_items = ctk.CTkFrame(self.slider_frame, fg_color="transparent")
        self.slider_items.pack(fill="x", padx=UIConfig.INNER_PAD, pady=(0, UIConfig.SMALL_PAD))

        self.action_frame = ctk.CTkFrame(
            self.action_panel,
            corner_radius=UIConfig.CARD_CORNER,
            fg_color=UIConfig.COLOR_CARD_BG,
            border_width=UIConfig.BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
        )

        self.action_title = ctk.CTkLabel(
            self.action_frame,
            text="Tac vu anh",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=UIConfig.COLOR_TEXT,
        )
        self.action_title.pack(anchor="w", padx=UIConfig.INNER_PAD, pady=(UIConfig.MAIN_PAD, 10))

        btn_row = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=UIConfig.INNER_PAD, pady=(0, UIConfig.MAIN_PAD))

        ctk.CTkButton(
            btn_row,
            text="Reset",
            command=self.reset_img,
            height=UIConfig.BUTTON_HEIGHT,
            corner_radius=UIConfig.BUTTON_CORNER,
            fg_color=UIConfig.COLOR_NEUTRAL,
            hover_color=UIConfig.COLOR_NEUTRAL_HOVER,
            text_color="#243447",
        ).pack(side="left", fill="x", expand=True, padx=(0, UIConfig.XSMALL_PAD))

        ctk.CTkButton(
            btn_row,
            text="Apply",
            command=self.apply_changes,
            height=UIConfig.BUTTON_HEIGHT,
            corner_radius=UIConfig.BUTTON_CORNER,
            fg_color=UIConfig.COLOR_SUCCESS,
            hover_color=UIConfig.COLOR_SUCCESS_HOVER,
            font=ctk.CTkFont(weight="bold"),
        ).pack(side="left", fill="x", expand=True, padx=4)

        ctk.CTkButton(
            btn_row,
            text="Download",
            command=self.download_image,
            height=UIConfig.BUTTON_HEIGHT,
            corner_radius=UIConfig.BUTTON_CORNER,
            fg_color=UIConfig.COLOR_PRIMARY,
            hover_color=UIConfig.COLOR_PRIMARY_HOVER,
            font=ctk.CTkFont(weight="bold"),
        ).pack(side="left", fill="x", expand=True, padx=(UIConfig.XSMALL_PAD, 0))

        self.slider_frame.pack_forget()
        self.action_frame.pack_forget()

    def show_tree(self):
        self.thumb_frame.pack_forget()
        self.tree_frame.pack(fill="both", expand=True)

    def show_thumbs(self):
        self.tree_frame.pack_forget()
        self.thumb_frame.pack(fill="both", expand=True)

    def hide_nav(self):
        self.rgb_nav_frame.pack_forget()

    def get_preview_size(self):
        self.root.update_idletasks()
        width = max(self.preview_canvas.winfo_width(), UIConfig.PREVIEW_MIN_WIDTH)
        height = max(self.preview_canvas.winfo_height(), UIConfig.PREVIEW_MIN_HEIGHT)
        return width, height

    def show_image_tk(self, tk_img):
        self.current_img = tk_img
        if self.preview_image_id is None:
            self.preview_image_id = self.preview_canvas.create_image(0, 0, image=self.current_img, anchor="nw")
        else:
            self.preview_canvas.itemconfigure(self.preview_image_id, image=self.current_img)
        self.preview_canvas.itemconfigure(self.preview_text_id, state="hidden")
        self.update_preview_canvas()

    def show_placeholder(self, title="Khu vuc xem anh", subtitle="Chon mot anh de bat dau."):
        self.current_img = None
        self.current_pil_image = None
        self.preview_zoom = 1.0
        if self.preview_image_id is not None:
            self.preview_canvas.delete(self.preview_image_id)
            self.preview_image_id = None
        self.preview_canvas.itemconfigure(self.preview_text_id, text=title, state="normal")
        self.image_title.configure(text=title)
        self.update_preview_canvas()

    def fit_preview_zoom(self):
        if self.current_pil_image is None:
            return 1.0
        canvas_w, canvas_h = self.get_preview_size()
        img_w, img_h = self.current_pil_image.size
        if img_w <= 0 or img_h <= 0:
            return 1.0
        return max(self.preview_min_zoom, min(min(canvas_w / img_w, canvas_h / img_h), self.preview_max_zoom))

    def reset_preview_zoom(self):
        if self.current_pil_image is None:
            return
        self.preview_zoom = self.fit_preview_zoom()
        self.render_preview_image()

    def render_preview_image(self):
        if self.current_pil_image is None:
            return
        img_w, img_h = self.current_pil_image.size
        scaled_size = (
            max(1, int(img_w * self.preview_zoom)),
            max(1, int(img_h * self.preview_zoom)),
        )
        rendered = self.current_pil_image.resize(scaled_size, Image.Resampling.LANCZOS)
        self.show_image_tk(ImageTk.PhotoImage(rendered))

    def update_preview_canvas(self):
        canvas_w, canvas_h = self.get_preview_size()

        if self.preview_image_id is None or self.current_img is None:
            self.preview_canvas.coords(self.preview_text_id, canvas_w / 2, canvas_h / 2)
            self.preview_canvas.configure(scrollregion=(0, 0, canvas_w, canvas_h))
            return

        img_w = self.current_img.width()
        img_h = self.current_img.height()
        offset_x = max((canvas_w - img_w) // 2, 0)
        offset_y = max((canvas_h - img_h) // 2, 0)
        self.preview_canvas.coords(self.preview_image_id, offset_x, offset_y)
        self.preview_canvas.configure(scrollregion=(0, 0, max(canvas_w, img_w), max(canvas_h, img_h)))

    def on_preview_canvas_configure(self, event):
        if self.current_pil_image is None:
            self.update_preview_canvas()
            return
        fit_zoom = self.fit_preview_zoom()
        if self.preview_zoom < fit_zoom:
            self.preview_zoom = fit_zoom
            self.render_preview_image()
        else:
            self.update_preview_canvas()

    def on_preview_mousewheel(self, event):
        self.preview_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_preview_shift_mousewheel(self, event):
        self.preview_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_preview_zoom(self, event):
        if self.current_pil_image is None:
            return
        zoom_step = 1.1 if event.delta > 0 else 0.9
        self.preview_zoom = max(self.preview_min_zoom, min(self.preview_zoom * zoom_step, self.preview_max_zoom))
        self.render_preview_image()

    def show_pil_image(self, pil_img):
        if pil_img is None:
            return
        self.current_pil_image = pil_img.copy()
        self.reset_preview_zoom()

    def show_cv_image(self, cv_img):
        pil_img = self.logic.cv_to_pil(cv_img)
        if pil_img is not None:
            self.show_pil_image(pil_img)

    def select_folder(self):
        path = filedialog.askdirectory()
        if not path:
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        root_node = self.tree.insert("", "end", text=os.path.basename(path), values=(path,))
        self.populate_tree(root_node, path)
        self.tree.item(root_node, open=True)
        self.show_placeholder("Thu muc da san sang")
        self.show_tree()

    def populate_tree(self, parent, path):
        try:
            for item in sorted(os.listdir(path)):
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
        for widget in self.thumb_scroll_frame.winfo_children():
            widget.destroy()
        self.thumb_buttons.clear()
        self.thumb_images.clear()

        folder_name = os.path.basename(path) or path
        self.thumb_title.configure(text=f"{folder_name}")

        if not images:
            ctk.CTkLabel(
                self.thumb_scroll_frame,
                text="Khong tim thay anh trong thu muc nay.",
                text_color="#64748b",
            ).grid(row=0, column=0, columnspan=self.col_count, padx=UIConfig.SMALL_PAD, pady=UIConfig.MAIN_PAD)
        else:
            for index, img in enumerate(images):
                pil_thumb = self.logic.get_thumbnail(img, size=UIConfig.THUMB_IMAGE_SIZE)
                if pil_thumb is None:
                    continue

                thumb = ctk.CTkImage(light_image=pil_thumb, dark_image=pil_thumb, size=pil_thumb.size)
                row = index // self.col_count
                col = index % self.col_count

                card = ctk.CTkFrame(
                    self.thumb_scroll_frame,
                    width=UIConfig.THUMB_CARD_WIDTH,
                    height=UIConfig.THUMB_CARD_HEIGHT,
                    corner_radius=UIConfig.GROUP_CORNER,
                    fg_color=UIConfig.COLOR_CARD_BG,
                    border_width=UIConfig.BORDER_WIDTH,
                    border_color=UIConfig.COLOR_BORDER_SOFT,
                )
                card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                card.grid_propagate(False)

                content = ctk.CTkFrame(card, fg_color="transparent")
                content.pack(fill="both", expand=True, padx=10, pady=10)

                image_label = ctk.CTkLabel(content, text="", image=thumb)
                image_label.pack(side="left", padx=(0, 10))

                text_label = ctk.CTkLabel(
                    content,
                    text=img,
                    text_color=UIConfig.COLOR_TEXT_ALT,
                    font=ctk.CTkFont(size=UIConfig.FONT_BODY),
                    wraplength=UIConfig.THUMB_TEXT_WRAP,
                    justify="left",
                    anchor="w",
                )
                text_label.pack(side="left", fill="both", expand=True)

                for widget in (card, content, image_label, text_label):
                    widget.bind("<Button-1>", lambda event, n=img: self.show_image(n))

                card.image = thumb
                self.thumb_buttons.append((img, card, text_label, image_label))
                self.thumb_images[img] = thumb

        self.show_thumbs()

    def show_action_bar(self):
        self.slider_frame.pack_forget()
        self.action_title.configure(text="Tac vu anh")
        self.action_frame.pack(side="top", fill="x", padx=UIConfig.XSMALL_PAD, pady=(UIConfig.XSMALL_PAD, UIConfig.INNER_PAD))

    def mark_selected_thumbnail(self, image_name):
        self.selected_thumb_name = image_name
        for name, btn, label, image_label in self.thumb_buttons:
            if name == image_name:
                btn.configure(fg_color=UIConfig.COLOR_PRIMARY_SOFT, border_color="#60a5fa")
                label.configure(text_color=UIConfig.COLOR_TEXT_BLUE)
            else:
                btn.configure(fg_color=UIConfig.COLOR_CARD_BG, border_color=UIConfig.COLOR_BORDER_SOFT)
                label.configure(text_color=UIConfig.COLOR_TEXT_ALT)

    def refresh_thumbnail(self, image_name):
        for name, btn, label, image_label in self.thumb_buttons:
            if name != image_name:
                continue

            pil_thumb = self.logic.get_thumbnail(image_name, size=UIConfig.THUMB_IMAGE_SIZE)
            if pil_thumb is None:
                return

            thumb = ctk.CTkImage(light_image=pil_thumb, dark_image=pil_thumb, size=pil_thumb.size)
            image_label.configure(image=thumb)
            image_label.image = thumb
            self.thumb_images[image_name] = thumb
            return

    def show_image(self, name):
        self.logic.load_image(name)
        pil_img = self.logic.cv_to_pil(self.logic.img_cv)
        if pil_img is not None:
            self.show_pil_image(pil_img)
            self.mark_selected_thumbnail(name)
            self.image_title.configure(text=name)
            self.current_op = None
            self.current_res_cv = None
            if hasattr(self, "show_action_bar"):
                self.show_action_bar()
        self.hide_nav()

    def update_rgb(self):
        if not hasattr(self, "rgb_imgs") or not self.rgb_imgs:
            return

        self.rgb_title.configure(text=UIConfig.RGB_TITLES[self.rgb_page], text_color=UIConfig.RGB_COLORS[self.rgb_page])
        self.current_res_cv = self.rgb_imgs[self.rgb_page]
        self.show_cv_image(self.rgb_imgs[self.rgb_page])

    def rgb_prev(self):
        if hasattr(self, "rgb_page") and self.rgb_page > 0:
            self.rgb_page -= 1
            self.update_rgb()

    def rgb_next(self):
        if hasattr(self, "rgb_page") and self.rgb_page < 2:
            self.rgb_page += 1
            self.update_rgb()
