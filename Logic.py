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
        valid_exts = ('.png', '.jpg', '.jpeg', '.bmp')
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

    def get_display_image(self, width, height, custom_cv_img=None):
        img_to_disp = custom_cv_img if custom_cv_img is not None else self.img_cv
        if img_to_disp is None:
            return None
        img_rgb = cv2.cvtColor(img_to_disp, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(img_rgb)
        if width < 10 or height < 10:
            width, height = 800, 600
        pil_image.thumbnail((width, height))
        return ImageTk.PhotoImage(pil_image)

    def save_image(self, path, cv_img):
        if cv_img is None: return False
        try:
            cv2.imwrite(path, cv_img)
            return True
        except:
            return False


class HW1Logic(ImageLogic):
    def get_RGB_Layer(self, width, height):
        if self.img_cv is None: return None
        b, g, r = cv2.split(self.img_cv)
        zeros = np.zeros_like(b)
        red_layer = cv2.merge([zeros, zeros, r])
        green_layer = cv2.merge([zeros, g, zeros])
        blue_layer = cv2.merge([b, zeros, zeros])

        tk_images = []
        for bgr_img in [red_layer, green_layer, blue_layer]:
            tk_images.append(self.get_display_image(width, height, bgr_img))
        return tk_images

    def get_Grayscale(self, width, height):
        if self.img_cv is None: return None
        gray_img = cv2.cvtColor(self.img_cv, cv2.COLOR_BGR2GRAY)
        gray_bgr = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)
        return self.get_display_image(width, height, gray_bgr)

    def get_Rotate_img(self, degree, scale):
        if self.img_cv is None: return None
        img = self.img_cv.copy()
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, degree, scale)
        return cv2.warpAffine(img, M, (w, h))

    def get_Crop_img(self):
        if self.img_cv is None: return None
        h, w = self.img_cv.shape[:2]
        crop_w, crop_h = w // 2, h // 2
        center_w, center_h = w // 2, h // 2
        x1 = center_w - crop_w // 2
        y1 = center_h - crop_h // 2
        x2 = center_w + crop_w // 2
        y2 = center_h + crop_h // 2
        return self.img_cv[y1:y2, x1:x2]


class HW2Logic(ImageLogic):
    def negative_transformation(self):
        if self.img_cv is None: return None
        return 255 - self.img_cv

    def log_transformation(self, c, base):
        if self.img_cv is None: return None
        img_float = np.float32(self.img_cv)
        if base <= 1.01: base = 1.01
        log_img = c * (np.log(1 + img_float) / np.log(base))
        return np.uint8(np.clip(log_img, 0, 255))

    def powerLaw_transformation(self, c, gamma):
        if self.img_cv is None: return None
        img_float = np.float32(self.img_cv) / 255.0
        power_img = c * (img_float ** gamma) * 255.0
        return np.uint8(np.clip(power_img, 0, 255))

    def histogram_equalization(self):
        if self.img_cv is None: return None
        yuv_img = cv2.cvtColor(self.img_cv, cv2.COLOR_BGR2YUV)
        yuv_img[:, :, 0] = cv2.equalizeHist(yuv_img[:, :, 0])
        return cv2.cvtColor(yuv_img, cv2.COLOR_YUV2BGR)

    def apply_local_hist(self, kernel_size):
        if self.img_cv is None: return None

        kernel_size = max(2, int(kernel_size))
        yuv_img = cv2.cvtColor(self.img_cv, cv2.COLOR_BGR2YUV)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(kernel_size, kernel_size))
        yuv_img[:, :, 0] = clahe.apply(yuv_img[:, :, 0])
        return cv2.cvtColor(yuv_img, cv2.COLOR_YUV2BGR)

    def piecewise_linear_transformation(self, r1, s1, r2, s2):
        if self.img_cv is None: return None
        r1, s1, r2, s2 = int(r1), int(s1), int(r2), int(s2)
        if r1 >= r2: r2 = r1 + 1
        if r2 > 255: r2 = 255

        lut = np.zeros(256, dtype=np.uint8)
        for r in range(256):
            if r <= r1:
                lut[r] = int(s1 / max(r1, 1) * r) if r1 > 0 else s1
            elif r <= r2:
                lut[r] = int(s1 + (s2 - s1) / (r2 - r1) * (r - r1))
            else:
                lut[r] = int(s2 + (255 - s2) / max(255 - r2, 1) * (r - r2))
        lut = np.clip(lut, 0, 255).astype(np.uint8)
        return cv2.LUT(self.img_cv, lut)

    def padding_convolution(self, A, kernel, padding=0):
        kh, kw = kernel.shape
        Ah, Aw = A.shape
        ph = kh // 2
        pw = kw // 2
        padded = np.pad(A,((ph, ph), (pw, pw)),mode='constant',constant_values=padding)
        result = np.zeros((Ah, Aw), dtype=np.float32)

        k = kernel
        p = padded
        r = result

        for i in range(Ah):
            for j in range(Aw):
                s = 0.0
                for m in range(kh):
                    row = i + m
                    for n in range(kw):
                        s += p[row, j + n] * k[m, n]
                r[i, j] = s
        return np.clip(r, 0, 255).astype(np.uint8)

    def _apply_kernel_to_image(self, kernel, use_padding=True):
        if self.img_cv is None: return None
        b, g, r = cv2.split(self.img_cv)

        b_filtered = self.padding_convolution(b.astype(np.float32), kernel, padding=0)
        g_filtered = self.padding_convolution( g.astype(np.float32), kernel, padding=0)
        r_filtered = self.padding_convolution(r.astype(np.float32), kernel, padding=0)

        return cv2.merge([b_filtered, g_filtered, r_filtered])

    def gaussian_filter(self, ksize, sigma):
        if self.img_cv is None: return None
        ksize = int(ksize)
        if ksize % 2 == 0: ksize += 1
        if ksize < 1: ksize = 1
        if sigma <= 0: sigma = 1.0

        # Tạo Gaussian kernel
        ax = np.arange(-(ksize // 2), ksize // 2 + 1)
        xx, yy = np.meshgrid(ax, ax)
        kernel = np.exp(-(xx ** 2 + yy ** 2) / (2 * sigma ** 2))
        kernel = kernel / kernel.sum()
        kernel = kernel.astype(np.float32)

        return cv2.filter2D(self.img_cv, -1, kernel)

    def box_filter(self, ksize):
        if self.img_cv is None: return None
        ksize = int(ksize)
        if ksize % 2 == 0: ksize += 1
        if ksize < 1: ksize = 1
        kernel = np.ones((ksize, ksize), dtype=np.float32)
        kernel /= kernel.sum()
        return cv2.filter2D(self.img_cv, -1, kernel)

    def median_filter(self, ksize):
        if self.img_cv is None: return None
        ksize = int(ksize)
        if ksize % 2 == 0: ksize += 1
        if ksize <= 0: ksize = 1
        return cv2.medianBlur(self.img_cv, ksize)

    def laplacian_filter(self, kernel_idx):
        if self.img_cv is None: return None
        kernels = [
            np.array([[0,  1, 0],
                      [1, -4, 1],
                      [0,  1, 0]], dtype=np.float32),

            np.array([[1,  1, 1],
                      [1, -8, 1],
                      [1,  1, 1]], dtype=np.float32),

            np.array([[ 0, -1,  0],
                      [-1,  4, -1],
                      [ 0, -1,  0]], dtype=np.float32),

            np.array([[-1, -1, -1],
                      [-1,  8, -1],
                      [-1, -1, -1]], dtype=np.float32),
        ]
        idx = int(kernel_idx)
        if idx < 0: idx = 0
        if idx > 3: idx = 3
        kernel = kernels[idx]

        gray = cv2.cvtColor(self.img_cv, cv2.COLOR_BGR2GRAY).astype(np.float32)
        filtered = self.padding_convolution(gray, kernel, padding=0)
        result = cv2.cvtColor(filtered, cv2.COLOR_GRAY2BGR)
        return result

    def sobel_filter(self):
        if self.img_cv is None: return None
        kx = np.array([[-1, 0, 1],
                       [-2, 0, 2],
                       [-1, 0, 1]], dtype=np.float32)
        ky = np.array([[-1, -2, -1],
                       [ 0,  0,  0],
                       [ 1,  2,  1]], dtype=np.float32)

        gray = cv2.cvtColor(self.img_cv, cv2.COLOR_BGR2GRAY).astype(np.float32)
        gx = self.padding_convolution(gray, kx, padding=0).astype(np.float32)
        gy = self.padding_convolution(gray, ky, padding=0).astype(np.float32)
        magnitude = np.clip(np.sqrt(gx**2 + gy**2), 0, 255).astype(np.uint8)
        return cv2.cvtColor(magnitude, cv2.COLOR_GRAY2BGR)

    def robert_filter(self):
        if self.img_cv is None: return None
        kx = np.array([[1,  0],
                       [0, -1]], dtype=np.float32)
        ky = np.array([[ 0, 1],
                       [-1, 0]], dtype=np.float32)

        gray = cv2.cvtColor(self.img_cv, cv2.COLOR_BGR2GRAY).astype(np.float32)
        gx = self.padding_convolution(gray, kx, padding=0).astype(np.float32)
        gy = self.padding_convolution(gray, ky, padding=0).astype(np.float32)
        magnitude = np.clip(np.sqrt(gx**2 + gy**2), 0, 255).astype(np.uint8)
        return cv2.cvtColor(magnitude, cv2.COLOR_GRAY2BGR)

    def prewitt_filter(self):
        if self.img_cv is None: return None
        kx = np.array([[-1, 0, 1],
                       [-1, 0, 1],
                       [-1, 0, 1]], dtype=np.float32)
        ky = np.array([[-1, -1, -1],
                       [ 0,  0,  0],
                       [ 1,  1,  1]], dtype=np.float32)

        gray = cv2.cvtColor(self.img_cv, cv2.COLOR_BGR2GRAY).astype(np.float32)
        gx = self.padding_convolution(gray, kx, padding=0).astype(np.float32)
        gy = self.padding_convolution(gray, ky, padding=0).astype(np.float32)
        magnitude = np.clip(np.sqrt(gx**2 + gy**2), 0, 255).astype(np.uint8)
        return cv2.cvtColor(magnitude, cv2.COLOR_GRAY2BGR)