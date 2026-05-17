import cv2
import numpy as np


class HW1Logic:
    def get_RGB_Layer(self, width=None, height=None):
        if self.img_cv is None:
            return None
        b, g, r = cv2.split(self.img_cv)
        zeros = np.zeros_like(b)
        red_layer = cv2.merge([zeros, zeros, r])
        green_layer = cv2.merge([zeros, g, zeros])
        blue_layer = cv2.merge([b, zeros, zeros])
        return [red_layer, green_layer, blue_layer]

    def get_Grayscale(self, width=None, height=None):
        if self.img_cv is None:
            return None
        gray_img = cv2.cvtColor(self.img_cv, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)

    def get_Rotate_img(self, degree, scale):
        if self.img_cv is None:
            return None
        img = self.img_cv.copy()
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, degree, scale)
        return cv2.warpAffine(img, matrix, (w, h))

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
