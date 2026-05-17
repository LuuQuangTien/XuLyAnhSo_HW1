import cv2
import numpy as np

class HW2Logic:
    # --- Grayscale Transformation ---
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

    # --- Convolution & Padding ---
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

    # --- Lowpass Filtering ---
    def gaussian_filter(self, ksize, sigma):
        if self.img_cv is None: return None
        ksize = int(ksize)
        if ksize % 2 == 0: ksize += 1
        if ksize < 1: ksize = 1
        if sigma <= 0: sigma = 1.0

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

    # --- Highpass Filtering ---
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
