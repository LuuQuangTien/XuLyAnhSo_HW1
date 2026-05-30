import os

import cv2
from PIL import Image

class BaseLogic:
    def __init__(self):
        self.img_cv = None
        self.current_folder = ""
        self.current_image_name = None
        self.current_image_path = None
        self.image_files = []
        self.thumbnails_cache = {}
        self.edited_images = {}

    def get_image_files(self, folder_path):
        if folder_path != self.current_folder:
            self.edited_images.clear()
        self.current_folder = folder_path
        valid_exts = (".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff")
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

        try:
            if img_name in self.edited_images:
                pil_img = self.cv_to_pil(self.edited_images[img_name])
            else:
                img_path = os.path.join(self.current_folder, img_name)
                pil_img = Image.open(img_path)

            if pil_img is None:
                return None

            pil_img.thumbnail(size)
            thumb = pil_img.copy()
            self.thumbnails_cache[cache_key] = thumb
            return thumb
        except Exception:
            return None

    def load_image(self, img_name):
        if not self.current_folder:
            return None
        self.current_image_name = img_name
        self.current_image_path = os.path.join(self.current_folder, img_name)
        if img_name in self.edited_images:
            self.img_cv = self.edited_images[img_name].copy()
            return self.img_cv

        self.img_cv = cv2.imread(self.current_image_path)
        return self.img_cv

    def apply_current_image(self, cv_img):
        if cv_img is None:
            return False

        if self.current_image_path is None:
            return False

        success = cv2.imwrite(self.current_image_path, cv_img)
        if not success:
            return False

        self.img_cv = cv_img.copy()
        if self.current_image_name:
            self.edited_images[self.current_image_name] = self.img_cv.copy()
            self.thumbnails_cache = {
                key: value
                for key, value in self.thumbnails_cache.items()
                if key[0] != self.current_image_name
            }
        return True

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