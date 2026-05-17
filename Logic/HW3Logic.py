import cv2
import numpy as np

class HW3Logic:
    def get_grayscale_image(self):
        if self.img_cv is None: return None
        if len(self.img_cv.shape) == 3:
            return cv2.cvtColor(self.img_cv, cv2.COLOR_BGR2GRAY)

        return self.img_cv.copy()

    def create_frequency_distance(self, rows, cols):
        crow, ccol = rows // 2, cols // 2
        x = np.arange(cols)
        y = np.arange(rows)
        u, v = np.meshgrid(x, y)
        return np.sqrt((u - ccol) ** 2 + (v - crow) ** 2)

    def fourier_transformation(self, gray_img):
        spectrum = np.fft.fft2(gray_img.astype(np.float32))
        return np.fft.fftshift(spectrum)

    def inverse_fourier_transformation(self, filtered_fshift):
        spectrum = np.fft.ifftshift(filtered_fshift)
        spatial = np.fft.ifft2(spectrum)
        return np.real(spatial)

    def normalize_inverse_fourier(self, spatial_img):
        normalized = cv2.normalize(spatial_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        return normalized.astype(np.uint8)

    def run_frequency_filter(self, mask):
        gray = self.get_grayscale_image()
        if gray is None:
            return None

        fshift = self.fourier_transformation(gray)
        filtered_fshift = fshift * mask
        spatial_img = self.inverse_fourier_transformation(filtered_fshift)
        output = self.normalize_inverse_fourier(spatial_img)
        return cv2.cvtColor(output, cv2.COLOR_GRAY2BGR)

    def ideal_mask(self, rows, cols, d0, highpass=False):
        distance = self.create_frequency_distance(rows, cols)
        mask = np.zeros((rows, cols), dtype=np.float32)
        mask[distance <= d0] = 1.0
        if highpass:
            mask = 1.0 - mask
        return mask

    def butterworth_mask(self, rows, cols, d0, order, highpass=False):
        distance = self.create_frequency_distance(rows, cols)
        distance = np.maximum(distance, 1e-5)
        mask = 1.0 / (1.0 + (distance / d0) ** (2 * order))
        if highpass:
            mask = 1.0 - mask
        return mask.astype(np.float32)

    def gaussian_mask(self, rows, cols, d0, highpass=False):
        distance = self.create_frequency_distance(rows, cols)
        mask = np.exp( -(distance ** 2) / (2 * (d0 ** 2)))
        if highpass:
            mask = 1.0 - mask
        return mask.astype(np.float32)

    def ideal_frequency_filter(self, D0, highpass=False):
        if self.img_cv is None: return None
        D0 = max(1, D0)
        rows, cols = self.img_cv.shape[:2]
        mask = self.ideal_mask(rows, cols, D0, highpass)
        return self.run_frequency_filter(mask)

    def butterworth_frequency_filter(self, D0, n, highpass=False):
        if self.img_cv is None: return None
        D0 = max(1, D0)
        n = max(1, n)
        rows, cols = self.img_cv.shape[:2]
        mask = self.butterworth_mask( rows, cols, D0, n, highpass)
        return self.run_frequency_filter(mask)

    def gaussian_frequency_filter(self, D0, highpass=False):
        if self.img_cv is None: return None
        D0 = max(1, D0)
        rows, cols = self.img_cv.shape[:2]
        mask = self.gaussian_mask( rows, cols, D0, highpass )
        return self.run_frequency_filter(mask)
