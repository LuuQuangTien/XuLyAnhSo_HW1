import os

import cv2
from PIL import Image


class BaseLogic:
    def __init__(self):
        self.img_cv = None
        self.current_folder = ""
        self.image_files = []
        self.thumbnails_cache = {}

    def get_image_files(self, folder_path):
        self.current_folder = folder_path
        valid_exts = (".png", ".jpg", ".jpeg", ".bmp")
        self.image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_exts)]
        self.thumbnails_cache.clear()
        return self.image_files

    def cv_to_pil(self, cv_img):
        if cv_img is None:
            return None

        if len(cv_img.shape) == 2:
            return Image.fromarray(cv_img)

        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb_img)

    def get_thumbnail(self, img_name, size=(120, 120)):
        cache_key = (img_name, size)
        if cache_key in self.thumbnails_cache:
            return self.thumbnails_cache[cache_key]

        img_path = os.path.join(self.current_folder, img_name)
        try:
            pil_img = Image.open(img_path)
            pil_img.thumbnail(size)
            thumb = pil_img.copy()
            self.thumbnails_cache[cache_key] = thumb
            return thumb
        except Exception:
            return None

    def load_image(self, img_name):
        if not self.current_folder:
            return None
        img_path = os.path.join(self.current_folder, img_name)
        self.img_cv = cv2.imread(img_path)
        return self.img_cv

    def get_display_image(self, width, height, custom_cv_img=None):
        img_to_disp = custom_cv_img if custom_cv_img is not None else self.img_cv
        if img_to_disp is None:
            return None

        pil_image = self.cv_to_pil(img_to_disp)
        if pil_image is None:
            return None

        if width < 10 or height < 10:
            width, height = 800, 600

        display = pil_image.copy()
        display.thumbnail((width, height))
        return display

    def save_image(self, path, cv_img):
        if cv_img is None:
            return False
        try:
            cv2.imwrite(path, cv_img)
            return True
        except Exception:
            return False
