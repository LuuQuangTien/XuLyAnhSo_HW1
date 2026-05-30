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
        self.preview_subtext_id = None
        self.preview_zoom = 1.0
        self.preview_min_zoom = 0.1
        self.preview_max_zoom = 8.0
        self.col_count = UIConfig.COL_COUNT

        ctk.set_appearance_mode("dark")
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

        self.tool_rail = ctk.CTkFrame(
            self.main_frame,
            width=UIConfig.TOOL_RAIL_WIDTH,
            fg_color=UIConfig.COLOR_TOOL_BG,
            corner_radius=UIConfig.PANEL_CORNER,
            border_width=UIConfig.BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
        )
        self.tool_rail.pack(side="left", fill="y")
        self.tool_rail.pack_propagate(False)

        self.left = ctk.CTkFrame(
            self.main_frame,
            width=UIConfig.LEFT_PANEL_WIDTH,
            corner_radius=UIConfig.PANEL_CORNER,
            fg_color=UIConfig.COLOR_LEFT_BG,
            border_width=UIConfig.BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
        )
        self.left.pack(side="left", fill="y", padx=(UIConfig.MAIN_PAD, 0))
        self.left.pack_propagate(False)

        self.center = ctk.CTkFrame(
            self.main_frame,
            fg_color=UIConfig.COLOR_RIGHT_BG,
            corner_radius=UIConfig.PANEL_CORNER,
            border_width=UIConfig.BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
        )
        self.center.pack(side="left", fill="both", expand=True, padx=(UIConfig.MAIN_PAD, UIConfig.MAIN_PAD))

        self.right = ctk.CTkFrame(
            self.main_frame,
            width=UIConfig.RIGHT_PANEL_WIDTH,
            corner_radius=UIConfig.PANEL_CORNER,
            fg_color=UIConfig.COLOR_LEFT_BG,
            border_width=UIConfig.BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
        )
        self.right.pack(side="left", fill="y")
        self.right.pack_propagate(False)

        self.build_tool_rail()
        self.build_sidebar_shell()
        self.build_preview_shell()
        self.build_action_shell()


    def show_active_hw_tools(self):
        if hasattr(self, "slider_frame"):
            self.slider_frame.pack_forget()
        if hasattr(self, "tool_group_widgets"):
            for widget in self.tool_group_widgets:
                widget.pack(fill="x", padx=2, pady=(0, 10))

    def build_tool_rail(self):
        # Open button at the top
        self.select_btn = ctk.CTkButton(
            self.tool_rail,
            text="Open",
            command=self.select_folder,
            height=UIConfig.BUTTON_HEIGHT,
            corner_radius=UIConfig.BUTTON_CORNER,
            fg_color=UIConfig.COLOR_TOOL_ACTIVE,
            hover_color=UIConfig.COLOR_PRIMARY_HOVER,
            font=ctk.CTkFont(size=UIConfig.FONT_BUTTON, weight="bold"),
        )
        self.select_btn.pack(fill="x", padx=6, pady=(12, 10))

        # Thin visual separator
        separator = ctk.CTkFrame(self.tool_rail, height=1, fg_color=UIConfig.COLOR_BORDER)
        separator.pack(fill="x", padx=8, pady=(0, 10))

        # HW1 to HW5 buttons in a neat, vertical layout
        self.hw_buttons = {}
        for i in range(1, 6):
            btn = ctk.CTkButton(
                self.tool_rail,
                text=f"HW{i}",
                height=32,
                corner_radius=UIConfig.BUTTON_CORNER,
                fg_color="transparent",
                hover_color=UIConfig.COLOR_TOOL_HOVER,
                text_color=UIConfig.COLOR_TEXT_ALT,
                border_width=1,
                border_color=UIConfig.COLOR_BORDER,
                font=ctk.CTkFont(size=UIConfig.FONT_BUTTON, weight="bold"),
                command=lambda n=i: self.select_hw(n)
            )
            btn.pack(fill="x", padx=6, pady=3)
            self.hw_buttons[i] = btn

        # Reset, Apply, Download action buttons packed at the bottom from the bottom up
        self.reset_btn = ctk.CTkButton(
            self.tool_rail,
            text="Reset",
            command=self.reset_img,
            height=UIConfig.BUTTON_HEIGHT,
            corner_radius=UIConfig.BUTTON_CORNER,
            fg_color=UIConfig.COLOR_NEUTRAL,
            hover_color=UIConfig.COLOR_NEUTRAL_HOVER,
            text_color=UIConfig.COLOR_TEXT_ALT,
            font=ctk.CTkFont(size=UIConfig.FONT_BUTTON, weight="bold"),
        )
        self.reset_btn.pack(side="bottom", fill="x", padx=6, pady=(3, 12))

        self.apply_btn = ctk.CTkButton(
            self.tool_rail,
            text="Apply",
            command=self.apply_changes,
            height=UIConfig.BUTTON_HEIGHT,
            corner_radius=UIConfig.BUTTON_CORNER,
            fg_color=UIConfig.COLOR_SUCCESS,
            hover_color=UIConfig.COLOR_SUCCESS_HOVER,
            text_color=UIConfig.COLOR_TEXT,
            font=ctk.CTkFont(size=UIConfig.FONT_BUTTON, weight="bold"),
        )
        self.apply_btn.pack(side="bottom", fill="x", padx=6, pady=3)

        self.download_btn = ctk.CTkButton(
            self.tool_rail,
            text="Download",
            command=self.download_image,
            height=UIConfig.BUTTON_HEIGHT,
            corner_radius=UIConfig.BUTTON_CORNER,
            fg_color=UIConfig.COLOR_PRIMARY,
            hover_color=UIConfig.COLOR_PRIMARY_HOVER,
            text_color=UIConfig.COLOR_TEXT,
            font=ctk.CTkFont(size=UIConfig.FONT_BUTTON, weight="bold"),
        )
        self.download_btn.pack(side="bottom", fill="x", padx=6, pady=3)

    def build_sidebar_shell(self):
        # Maximized container for folders tree and thumbnails
        self.nav_container = ctk.CTkFrame(
            self.left,
            corner_radius=UIConfig.PANEL_CORNER,
            fg_color=UIConfig.COLOR_CARD_BG,
            border_width=UIConfig.BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
        )
        self.nav_container.pack(fill="both", expand=True, padx=UIConfig.INNER_PAD, pady=UIConfig.INNER_PAD)

        self.tree_frame = ctk.CTkFrame(self.nav_container, fg_color="transparent")
        self._build_tree_view()

        self.thumb_frame = ctk.CTkFrame(self.nav_container, fg_color="transparent")
        self._build_thumbnail_view()

        # Sleek compatibility status fields
        self.browser_status = ctk.CTkLabel(
            self.left,
            text="No file selected",
            text_color=UIConfig.COLOR_TEXT_MUTED,
            font=ctk.CTkFont(size=UIConfig.FONT_SMALL, weight="bold"),
            anchor="w",
        )
        self.browser_status.pack(fill="x", padx=UIConfig.INNER_PAD, pady=(0, UIConfig.INNER_PAD))

        # Hidden browser footer placeholder to satisfy reference constraints in other tools
        self.browser_footer = self.left
        self.browser_hint = ctk.CTkLabel(self.left, text="")  # Hidden label

        self.show_tree()

    def _build_tree_view(self):
        ctk.CTkLabel(
            self.tree_frame,
            text="Folders",
            font=ctk.CTkFont(size=UIConfig.FONT_GROUP, weight="bold"),
            text_color=UIConfig.COLOR_TEXT,
        ).pack(anchor="w", padx=14, pady=(14, UIConfig.XSMALL_PAD))

        tree_wrap = ctk.CTkFrame(
            self.tree_frame,
            fg_color=UIConfig.COLOR_SUBTLE_BG,
            corner_radius=UIConfig.SMALL_CORNER,
        )
        tree_wrap.pack(fill="both", expand=True, padx=UIConfig.SMALL_PAD, pady=(0, UIConfig.SMALL_PAD))

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Custom.Treeview",
            background=UIConfig.COLOR_SUBTLE_BG,
            fieldbackground=UIConfig.COLOR_SUBTLE_BG,
            foreground=UIConfig.COLOR_TEXT_ALT,
            rowheight=UIConfig.TREE_ROW_HEIGHT,
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 10),
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", "#25406a")],
            foreground=[("selected", "#f8fbff")],
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
            width=82,
            height=UIConfig.SMALL_BUTTON_HEIGHT,
            command=self.show_tree,
            corner_radius=UIConfig.XS_CORNER,
            fg_color=UIConfig.COLOR_SECONDARY_SOFT,
            hover_color=UIConfig.COLOR_SECONDARY_SOFT_HOVER,
            text_color=UIConfig.COLOR_TEXT_ALT,
        ).pack(side="left")

        self.thumb_title = ctk.CTkLabel(
            top_bar,
            text="Assets",
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
        self.top_toolbar = ctk.CTkFrame(
            self.center,
            fg_color=UIConfig.COLOR_CARD_BG,
            corner_radius=UIConfig.GROUP_CORNER,
            border_width=UIConfig.BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
        )
        self.top_toolbar.pack(fill="x", padx=UIConfig.SECTION_PAD_X, pady=(16, 10))

        self._add_toolbar_chip(self.top_toolbar, "Zoom", "Fit")
        self._add_toolbar_chip(self.top_toolbar, "Mode", "Preview")
        self._add_toolbar_chip(self.top_toolbar, "Canvas", "RGB")
        self.zoom_label = self._add_toolbar_chip(self.top_toolbar, "Scale", "100%")

        self.preview_panel = ctk.CTkFrame(self.center, fg_color="transparent")
        self.preview_panel.pack(fill="both", expand=True, padx=UIConfig.SECTION_PAD_X, pady=(0, UIConfig.SECTION_PAD_Y))

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
            text="No image loaded",
            font=ctk.CTkFont(size=UIConfig.FONT_SECTION, weight="bold"),
            text_color=UIConfig.COLOR_TEXT,
        )
        self.image_title.pack(side="left", anchor="w")

        self.image_meta = ctk.CTkLabel(
            self.image_info_bar,
            text="Preview workspace",
            font=ctk.CTkFont(size=11),
            text_color=UIConfig.COLOR_TEXT_MUTED,
        )
        self.image_meta.pack(side="right", anchor="e")

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
            text="Canvas",
            fill=UIConfig.COLOR_TEXT_ALT,
            font=("Segoe UI", 24, "bold"),
            anchor="center",
        )
        self.preview_subtext_id = self.preview_canvas.create_text(
            0,
            0,
            text="Open a folder and choose an image to start editing",
            fill=UIConfig.COLOR_TEXT_FAINT,
            font=("Segoe UI", 12),
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
            border_width=UIConfig.BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
        )
        self.rgb_title = ctk.CTkLabel(
            self.rgb_nav_frame,
            text="",
            text_color=UIConfig.COLOR_TEXT,
            font=ctk.CTkFont(size=UIConfig.FONT_GROUP, weight="bold"),
        )
        self.rgb_title.pack(pady=(UIConfig.SMALL_PAD, 6))

        nav = ctk.CTkFrame(self.rgb_nav_frame, fg_color="transparent")
        nav.pack(fill="x", padx=14, pady=(0, UIConfig.SMALL_PAD))

        ctk.CTkButton(
            nav,
            text="Previous",
            command=self.rgb_prev,
            height=UIConfig.SMALL_BUTTON_HEIGHT,
            corner_radius=UIConfig.XS_CORNER,
            fg_color=UIConfig.COLOR_PRIMARY_SOFT,
            hover_color=UIConfig.COLOR_PRIMARY_SOFT_HOVER,
            text_color=UIConfig.COLOR_TEXT_BLUE,
        ).pack(side="left", fill="x", expand=True, padx=(0, UIConfig.XSMALL_PAD))

        ctk.CTkButton(
            nav,
            text="Next",
            command=self.rgb_next,
            height=UIConfig.SMALL_BUTTON_HEIGHT,
            corner_radius=UIConfig.XS_CORNER,
            fg_color=UIConfig.COLOR_PRIMARY_SOFT,
            hover_color=UIConfig.COLOR_PRIMARY_SOFT_HOVER,
            text_color=UIConfig.COLOR_TEXT_BLUE,
        ).pack(side="left", fill="x", expand=True)

    def _add_toolbar_chip(self, parent, label, value):
        chip = ctk.CTkFrame(parent, fg_color="transparent")
        chip.pack(side="left", padx=(14, 0), pady=10)

        ctk.CTkLabel(
            chip,
            text=label.upper(),
            text_color=UIConfig.COLOR_TEXT_FAINT,
            font=ctk.CTkFont(size=9, weight="bold"),
        ).pack(anchor="w")

        value_label = ctk.CTkLabel(
            chip,
            text=value,
            text_color=UIConfig.COLOR_TEXT_ALT,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        value_label.pack(anchor="w")
        return value_label

    def build_action_shell(self):
        self.action_panel = ctk.CTkScrollableFrame(
            self.right,
            corner_radius=UIConfig.PANEL_CORNER,
            fg_color=UIConfig.COLOR_SUBTLE_BG,
            border_width=UIConfig.BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
        )
        self.action_panel.pack(fill="both", expand=True, padx=UIConfig.INNER_PAD, pady=UIConfig.INNER_PAD)
        self.tool_group_widgets = []

        self.slider_frame = ctk.CTkFrame(
            self.action_panel,
            corner_radius=UIConfig.CARD_CORNER,
            fg_color=UIConfig.COLOR_CARD_BG,
            border_width=UIConfig.BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
        )
        self.slider_frame.pack_forget()
        self.back_btn = ctk.CTkButton(
            self.slider_frame,
            text="← Back to Tools",
            height=UIConfig.SMALL_BUTTON_HEIGHT,
            corner_radius=UIConfig.XS_CORNER,
            fg_color=UIConfig.COLOR_BUTTON_SOFT,
            hover_color=UIConfig.COLOR_BUTTON_SOFT_HOVER,
            text_color=UIConfig.COLOR_TEXT_BLUE,
            font=ctk.CTkFont(size=UIConfig.FONT_BUTTON, weight="bold"),
            command=self.show_active_hw_tools
        )
        self.back_btn.pack(anchor="w", padx=UIConfig.INNER_PAD, pady=(UIConfig.INNER_PAD, 6))

        self.slider_header = ctk.CTkLabel(
            self.slider_frame,
            text="Adjustments",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=UIConfig.COLOR_TEXT,
        )
        self.slider_header.pack(anchor="w", padx=UIConfig.INNER_PAD, pady=(2, 6))
        self.action_title = ctk.CTkLabel(self.slider_frame, text="")
        self.action_frame = ctk.CTkFrame(self.slider_frame, fg_color="transparent")

        self.slider_items = ctk.CTkFrame(self.slider_frame, fg_color="transparent")
        self.slider_items.pack(fill="x", padx=UIConfig.INNER_PAD, pady=(0, UIConfig.INNER_PAD))

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
        self.preview_canvas.itemconfigure(self.preview_subtext_id, state="hidden")
        self.update_preview_canvas()

    def show_placeholder(self, title="Canvas", subtitle="Open a folder and choose an image to start editing"):
        self.current_img = None
        self.current_pil_image = None
        self.preview_zoom = 1.0
        if self.preview_image_id is not None:
            self.preview_canvas.delete(self.preview_image_id)
            self.preview_image_id = None
        self.preview_canvas.itemconfigure(self.preview_text_id, text=title, state="normal")
        self.preview_canvas.itemconfigure(self.preview_subtext_id, text=subtitle, state="normal")
        self.image_title.configure(text=title)
        self.image_meta.configure(text="Preview workspace")
        self.browser_status.configure(text="No file selected")
        self.update_zoom_label()
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
        self.update_zoom_label()
        self.image_meta.configure(text=f"{img_w} x {img_h}px")

    def update_zoom_label(self):
        if hasattr(self, "zoom_label"):
            self.zoom_label.configure(text=f"{int(self.preview_zoom * 100)}%")

    def update_preview_canvas(self):
        canvas_w, canvas_h = self.get_preview_size()

        if self.preview_image_id is None or self.current_img is None:
            self.preview_canvas.coords(self.preview_text_id, canvas_w / 2, (canvas_h / 2) - 14)
            self.preview_canvas.coords(self.preview_subtext_id, canvas_w / 2, (canvas_h / 2) + 18)
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
        self.browser_status.configure(text=os.path.basename(path) or path)
        self.browser_hint.configure(text="Thu muc da nap. Chon mot folder con de hien thumbnail anh.")
        self.show_placeholder("Folder Ready", "Chon mot image asset o browser ben trai.")
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
        self.thumb_title.configure(text=folder_name)
        self.browser_status.configure(text=folder_name)
        self.browser_hint.configure(text="Danh sach thumbnail da san sang. Click vao mot anh de dua len canvas.")

        if not images:
            ctk.CTkLabel(
                self.thumb_scroll_frame,
                text="Khong tim thay anh trong thu muc nay.",
                text_color=UIConfig.COLOR_TEXT_MUTED,
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
                card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
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
        self.show_active_hw_tools()

    def mark_selected_thumbnail(self, image_name):
        self.selected_thumb_name = image_name
        for name, btn, label, image_label in self.thumb_buttons:
            if name == image_name:
                btn.configure(fg_color=UIConfig.COLOR_PRIMARY_SOFT, border_color=UIConfig.COLOR_PRIMARY)
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
            self.browser_status.configure(text=name)
            self.browser_hint.configure(text="Anh hien dang duoc preview. Chon effect de thay doi va Apply de ghi vao file goc.")
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
