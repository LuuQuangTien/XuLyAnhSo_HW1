import os
import cv2
import numpy as np
from PIL import Image, ImageTk

class ImageLogic:
    def __init__(self):
        self.img_cv = None
        self.current_folder = ""
        self.image_files = []
        self.thumbnails_cache = {}

    def get_image_files(self, folder_path):
        self.current_folder = folder_path
        valid_exts = ('.png', '.jpg', '.jpeg')
        self.image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_exts)]
        self.thumbnails_cache.clear()
        return self.image_files

    def get_thumbnail(self, img_name, size=(80, 80)):
        if img_name in self.thumbnails_cache:
            return self.thumbnails_cache[img_name]
            
        img_path = os.path.join(self.current_folder, img_name)
        try:
            pil_img = Image.open(img_path)
            pil_img.thumbnail(size)
            tk_thumb = ImageTk.PhotoImage(pil_img)
            self.thumbnails_cache[img_name] = tk_thumb
            return tk_thumb
        except Exception as e:
            return None

    def load_image(self, img_name):
        if not self.current_folder:
            return None
        img_path = os.path.join(self.current_folder, img_name)
        self.img_cv = cv2.imread(img_path)
        return self.img_cv

    def get_display_image(self, width, height):
        if self.img_cv is None:
            return None
        img_rgb = cv2.cvtColor(self.img_cv, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(img_rgb)
        if width < 10 or height < 10:
            width, height = 800, 600
        pil_image.thumbnail((width, height))
        return ImageTk.PhotoImage(pil_image)

    def get_RGB_Layer(self, width, height):
        if self.img_cv is None:
            return None
        b, g, r = cv2.split(self.img_cv)
        zeros = np.zeros_like(b)
        
        red_layer = cv2.merge([zeros, zeros, r])
        green_layer = cv2.merge([zeros, g, zeros])
        blue_layer = cv2.merge([b, zeros, zeros])
        
        tk_images = []
        for bgr_img in [red_layer, green_layer, blue_layer]:
            rgb_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_img)
            if width >= 10 and height >= 10:
                pil_img.thumbnail((width, height))
            tk_images.append(ImageTk.PhotoImage(pil_img))
            
        return tk_images
    
    def get_Grayscale(self, width, height):
        if self.img_cv is None:
            return None
        gray_img = cv2.cvtColor(self.img_cv, cv2.COLOR_BGR2GRAY)
        pil_img = Image.fromarray(gray_img)
        if width >= 10 and height >= 10:
            pil_img.thumbnail((width, height))
        return ImageTk.PhotoImage(pil_img)

    def get_Rotate_img(self, degree):
        if self.img_cv is None:
            return None

        img = self.img_cv.copy()
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)

        M = cv2.getRotationMatrix2D(center, degree, 1.0)
        rotated_img = cv2.warpAffine(img, M, (w, h))

        return rotated_img

    def get_Crop_img(self):
        if self.img_cv is None:
            return None

        h, w = self.img_cv.shape[:2]
        crop_w, crop_h = w // 2, h // 2
        center_w, center_h = w // 2, h // 2

        x1 = center_w - crop_w // 2
        y1 = center_h - crop_h // 2
        x2 = center_w + crop_w // 2
        y2 = center_h + crop_h // 2

        return self.img_cv[y1:y2, x1:x2]