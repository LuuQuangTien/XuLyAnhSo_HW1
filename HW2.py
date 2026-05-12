import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from UI import UI
from Logic import HW2Logic

class HW2(UI):
    def __init__(self, root):
        self.current_op = None
        self.current_res_cv = None
        self.active_sliders = {}
        super().__init__(root)
        self.logic = HW2Logic()

    def setup_buttons(self):
        self.btn_canvas = tk.Canvas(self.left, height=350)
        self.btn_scrollbar = ttk.Scrollbar(self.left, orient="vertical", command=self.btn_canvas.yview)
        self.btn_frame = tk.Frame(self.btn_canvas)

        self.btn_frame.bind(
            "<Configure>",
            lambda e: self.btn_canvas.configure(scrollregion=self.btn_canvas.bbox("all"))
        )

        self.btn_canvas.create_window((0, 0), window=self.btn_frame, anchor="nw", width=250)
        self.btn_canvas.configure(yscrollcommand=self.btn_scrollbar.set)

        self.btn_canvas.pack(side="top", fill="both", expand=True, pady=5)
        self.btn_scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            self.btn_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mousewheel(event):
            self.btn_canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
        def _unbind_mousewheel(event):
            self.btn_canvas.unbind_all("<MouseWheel>")
            
        self.btn_canvas.bind("<Enter>", _bind_mousewheel)
        self.btn_canvas.bind("<Leave>", _unbind_mousewheel)

        tk.Label(self.btn_frame, text="Grayscale Transformation", bg="lightgray").pack(fill=tk.X, pady=(0, 5))
        tk.Button(self.btn_frame, text="Âm ảnh", command=lambda: self.set_op('negative')).pack(fill=tk.X, pady=2)
        tk.Button(self.btn_frame, text="Biến đổi Logarit", command=lambda: self.set_op('log')).pack(fill=tk.X, pady=2)
        tk.Button(self.btn_frame, text="Luật luỹ thừa (Gamma)", command=lambda: self.set_op('gamma')).pack(fill=tk.X, pady=2)
        tk.Button(self.btn_frame, text="Histogram equalization", command=lambda: self.set_op('hist')).pack(fill=tk.X, pady=2)
        tk.Button(self.btn_frame, text="Local hist processing", command=lambda: self.set_op('local_hist')).pack(fill=tk.X, pady=2)

        tk.Label(self.btn_frame, text="Lowpass Filtering (Làm trơn)", bg="lightgray").pack(fill=tk.X, pady=(15, 5))
        tk.Button(self.btn_frame, text="Lọc Gauss", command=lambda: self.set_op('gaussian')).pack(fill=tk.X, pady=2)
        tk.Button(self.btn_frame, text="Lọc trung bình", command=lambda: self.set_op('box')).pack(fill=tk.X, pady=2)
        tk.Button(self.btn_frame, text="Lọc trung vị", command=lambda: self.set_op('median')).pack(fill=tk.X, pady=2)

        tk.Label(self.btn_frame, text="Highpass Filtering  (Làm sắc nét)", bg="lightgray").pack(fill=tk.X, pady=(15, 5))
        tk.Button(self.btn_frame, text="Laplace K1 (0,1,0/1,-4,1)", command=lambda: self.set_op('laplacian_0')).pack(fill=tk.X, pady=2)
        tk.Button(self.btn_frame, text="Laplace K2 (1,1,1/1,-8,1)", command=lambda: self.set_op('laplacian_1')).pack(fill=tk.X, pady=2)
        tk.Button(self.btn_frame, text="Laplace K3 (0,-1,0/-1,4,-1)", command=lambda: self.set_op('laplacian_2')).pack(fill=tk.X, pady=2)
        tk.Button(self.btn_frame, text="Laplace K4 (-1,-1,-1/-1,8,-1)", command=lambda: self.set_op('laplacian_3')).pack(fill=tk.X, pady=2)
        tk.Button(self.btn_frame, text="Lọc Sobel", command=lambda: self.set_op('sobel')).pack(fill=tk.X, pady=2)
        tk.Button(self.btn_frame, text="Lọc Robert", command=lambda: self.set_op('robert')).pack(fill=tk.X, pady=2)
        tk.Button(self.btn_frame, text="Lọc Prewitt", command=lambda: self.set_op('prewitt')).pack(fill=tk.X, pady=2)

        self.slider_frame = tk.Frame(self.right)
        self.action_frame = tk.Frame(self.right)
        tk.Button(self.action_frame, text="Reset", command=self.reset_img).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        tk.Button(self.action_frame, text="Apply", command=self.apply_changes, bg="#48d141").pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        tk.Button(self.action_frame, text="Download", command=self.download_image, bg="#418cd1").pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.slider_frame.pack_forget()
        self.action_frame.pack_forget()

    def set_op(self, op_name):
        if self.logic.img_cv is None:
            messagebox.showwarning("Error", "Chọn ảnh trước")
            return

        self.current_op = op_name
        self.hide_nav()
        for widget in self.slider_frame.winfo_children():
            widget.destroy()
        self.active_sliders.clear()
        show_slider = True

        if op_name in ['negative', 'hist', 'sobel', 'robert', 'prewitt'] or op_name.startswith('laplacian_'):
            show_slider = False
        elif op_name == 'log':
            self.add_slider('c', "C Value (Log)", 1.0, 100.0, 40.0)
            self.add_slider('base', "Base", 1.01, 20.0, 2.71)
        elif op_name == 'gamma':
            self.add_slider('c', "C Value", 0.1, 5.0, 1.0)
            self.add_slider('gamma', "Gamma Value", 0.1, 5.0, 1.0)
        elif op_name == 'local_hist':
            self.add_slider('kernel_size', "Kernel Size", 3, 31, 7, is_int=True)
        elif op_name == 'piecewise':
            self.add_slider('r1', "r1", 0, 255, 50, is_int=True)
            self.add_slider('s1', "s1", 0, 255, 20, is_int=True)
            self.add_slider('r2', "r2", 0, 255, 200, is_int=True)
            self.add_slider('s2', "s2", 0, 255, 230, is_int=True)
        elif op_name in ['box', 'median']:
            self.add_slider('ksize', "Kernel Size", 1, 31, 3, is_int=True)
        elif op_name == 'gaussian':
            self.add_slider('ksize', "Kernel Size", 1, 31, 3, is_int=True)
            self.add_slider('sigma', "Sigma", 0.1, 10.0, 1.0)


        self.action_frame.pack_forget()
        self.slider_frame.pack_forget()

        self.action_frame.pack(side="bottom", fill=tk.X, pady=10)
        
        if show_slider:
            self.slider_frame.pack(side="bottom", fill=tk.X, pady=(10, 0))
        self.on_slide()

    def add_slider(self, key, label_text, from_val, to_val, default_val, is_int=False):
        frame = tk.Frame(self.slider_frame)
        frame.pack(fill=tk.X, pady=2)
        tk.Label(frame, text=label_text, width=15, anchor="w").pack(side=tk.LEFT)
        var = tk.DoubleVar(value=default_val)
        
        val_str = f"{int(default_val)}" if is_int else f"{default_val:.2f}"
        val_label = tk.Label(frame, text=val_str, width=5)
        
        def _update_label(val):
            v = float(val)
            if is_int:
                v_int = int(v)
                if key == 'ksize' and v_int % 2 == 0:
                    v_int += 1
                val_label.config(text=f"{v_int}")
            else:
                val_label.config(text=f"{v:.2f}")
            self.on_slide()

        scale = ttk.Scale(frame, variable=var, from_=from_val, to=to_val, command=_update_label)
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        val_label.pack(side=tk.LEFT, padx=(5, 0))
        self.active_sliders[key] = var

    def on_slide(self, *args):
        if self.current_op is None or self.logic.img_cv is None:
            return
        vals = {k: v.get() for k, v in self.active_sliders.items()}

        res_cv = None
        if self.current_op == 'negative':
            res_cv = self.logic.negative_transformation()
        elif self.current_op == 'log':
            res_cv = self.logic.log_transformation(c=vals.get('c', 40.0), base=vals.get('base', 2.71))
        elif self.current_op == 'gamma':
            res_cv = self.logic.powerLaw_transformation(c=vals.get('c', 1.0), gamma=vals.get('gamma', 1.0))
        elif self.current_op == 'hist':
            res_cv = self.logic.histogram_equalization()
        elif self.current_op == 'local_hist':
            res_cv = self.logic.apply_local_hist(kernel_size=vals.get('kernel_size', 7))
        elif self.current_op == 'piecewise':
            res_cv = self.logic.piecewise_linear_transformation(
                r1=vals.get('r1', 50), s1=vals.get('s1', 20),
                r2=vals.get('r2', 200), s2=vals.get('s2', 230)
            )
        elif self.current_op == 'gaussian':
            res_cv = self.logic.gaussian_filter(ksize=vals.get('ksize', 3), sigma=vals.get('sigma', 1.0))
        elif self.current_op == 'box':
            res_cv = self.logic.box_filter(ksize=vals.get('ksize', 3))
        elif self.current_op == 'median':
            res_cv = self.logic.median_filter(ksize=vals.get('ksize', 3))
        elif self.current_op.startswith('laplacian_'):
            idx = int(self.current_op.split('_')[1])
            res_cv = self.logic.laplacian_filter(kernel_idx=idx)
        elif self.current_op == 'sobel':
            res_cv = self.logic.sobel_filter()
        elif self.current_op == 'robert':
            res_cv = self.logic.robert_filter()
        elif self.current_op == 'prewitt':
            res_cv = self.logic.prewitt_filter()

        if res_cv is not None:
            self.current_res_cv = res_cv
            self.show_cv_image(res_cv)

    def reset_img(self):
        self.current_res_cv = None
        self.show_cv_image(self.logic.img_cv)

    def apply_changes(self):
        if self.current_res_cv is not None:
            self.logic.img_cv = self.current_res_cv
            messagebox.showinfo("Success", "Đã lưu đè thay đổi lên ảnh hiện tại!")
            img = self.logic.get_display_image(800, 600)
            if img:
                self.show_image_tk(img)
            self.slider_frame.pack_forget()
            self.action_frame.pack_forget()
            self.current_op = None

    def download_image(self):
        if self.current_res_cv is None:
            return
            
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg"), ("All Files", "*.*")]
        )
        if path:
            success = self.logic.save_image(path, self.current_res_cv)
            if success:
                messagebox.showinfo("Success", f"Đã lưu ảnh tại:\n{path}")
            else:
                messagebox.showerror("Error", "Không thể lưu ảnh.")