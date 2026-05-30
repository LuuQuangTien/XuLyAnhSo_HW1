import cv2
import numpy as np

class HW4Logic:
    STRUCTURING_ELEMENT_MAP = {
        "rect": cv2.MORPH_RECT,
        "ellipse": cv2.MORPH_ELLIPSE,
        "cross": cv2.MORPH_CROSS,
    }

    def _normalize_kernel_size(self, ksize):
        ksize = max(1, int(round(ksize)))
        if ksize % 2 == 0:
            ksize += 1
        return ksize

    def _to_binary(self, img):
        if img is None:
            return None
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        return binary

    def get_structuring_element(self, ksize=3, shape="rect"):
        ksize = self._normalize_kernel_size(ksize)
        shape_key = str(shape).lower()
        morph_shape = self.STRUCTURING_ELEMENT_MAP.get(shape_key, cv2.MORPH_RECT)
        return cv2.getStructuringElement(morph_shape, (ksize, ksize))

    def get_custom_structuring_element(self, kernel_matrix=None, size=3):
        size = 5 if int(size) == 5 else 3
        if kernel_matrix is None:
            return np.ones((size, size), dtype=np.uint8)

        kernel = np.array(kernel_matrix, dtype=np.float32)
        if kernel.ndim != 2:
            return np.ones((size, size), dtype=np.uint8)

        if kernel.shape[0] != kernel.shape[1] or kernel.shape[0] not in (3, 5):
            return np.ones((size, size), dtype=np.uint8)

        kernel = np.where(kernel > 0, 1, 0).astype(np.uint8)
        if not np.any(kernel):
            kernel = np.ones((kernel.shape[0], kernel.shape[1]), dtype=np.uint8)
        return kernel

    def _get_kernel(self, ksize, shape, kernel_matrix=None):
        if str(shape).lower() == "custom":
            return self.get_custom_structuring_element(kernel_matrix=kernel_matrix, size=ksize)
        else:
            return self.get_structuring_element(ksize=ksize, shape=shape)

    def apply_morphology(self, operation, ksize=3, shape="rect", iterations=1, kernel_matrix=None):
        if self.img_cv is None:
            return None
        img = self._to_binary(self.img_cv)
        kernel = self._get_kernel(ksize, shape, kernel_matrix)
        iterations = max(1, int(round(iterations)))

        if operation == "erosion":
            return cv2.erode(img, kernel, iterations=iterations)
        if operation == "dilation":
            return cv2.dilate(img, kernel, iterations=iterations)
        if operation == "opening":
            return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel, iterations=iterations)
        if operation == "closing":
            return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel, iterations=iterations)
        return None

    def erosion(self, ksize=3, shape="rect", iterations=1, kernel_matrix=None):
        return self.apply_morphology("erosion", ksize=ksize, shape=shape, iterations=iterations, kernel_matrix=kernel_matrix)

    def dilation(self, ksize=3, shape="rect", iterations=1, kernel_matrix=None):
        return self.apply_morphology("dilation", ksize=ksize, shape=shape, iterations=iterations, kernel_matrix=kernel_matrix)

    def opening(self, ksize=3, shape="rect", iterations=1, kernel_matrix=None):
        return self.apply_morphology("opening", ksize=ksize, shape=shape, iterations=iterations, kernel_matrix=kernel_matrix)

    def closing(self, ksize=3, shape="rect", iterations=1, kernel_matrix=None):
        return self.apply_morphology("closing", ksize=ksize, shape=shape, iterations=iterations, kernel_matrix=kernel_matrix)

    def hitmiss(self, kernel_matrix=None):
        if self.img_cv is None:
            return None
        img = self._to_binary(self.img_cv)

        if kernel_matrix is None:
            kernel = np.array([[-1, -1, -1],
                               [-1,  1, -1],
                               [-1, -1, -1]], dtype=np.int32)
        else:
            kernel = np.array(kernel_matrix, dtype=np.int32)

        return cv2.morphologyEx(img, cv2.MORPH_HITMISS, kernel)

    def boundary_extraction(self, ksize=3, shape="rect", kernel_matrix=None):
        if self.img_cv is None:
            return None
        img = self._to_binary(self.img_cv)
        kernel = self._get_kernel(ksize, shape, kernel_matrix)
        eroded = cv2.erode(img, kernel, iterations=1)
        return cv2.subtract(img, eroded)

    def region_filling(self, seed_x=-1, seed_y=-1):
        if self.img_cv is None:
            return None
        img = self._to_binary(self.img_cv)
        inverted = cv2.bitwise_not(img)

        h, w = img.shape[:2]
        mask = np.zeros((h + 2, w + 2), np.uint8)
        flood = inverted.copy()

        if seed_x >= 0 and seed_y >= 0 and seed_x < w and seed_y < h:
            cv2.floodFill(flood, mask, (int(seed_x), int(seed_y)), 255)
            filled_holes = cv2.bitwise_xor(flood, inverted)
            result = cv2.bitwise_or(img, filled_holes)
        else:
            cv2.floodFill(flood, mask, (0, 0), 0)
            cv2.floodFill(flood, None, (w - 1, 0), 0)
            cv2.floodFill(flood, None, (0, h - 1), 0)
            cv2.floodFill(flood, None, (w - 1, h - 1), 0)
            result = cv2.bitwise_or(img, flood)

        return result

    def connected_components(self):
        if self.img_cv is None:
            return None
        img = self._to_binary(self.img_cv)
        num_labels, labels = cv2.connectedComponents(img)
        if num_labels <= 1:
            return img

        output = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        for label in range(1, num_labels):
            hue = int(180 * label / num_labels)
            color_hsv = np.uint8([[[hue, 200, 230]]])
            color_bgr = cv2.cvtColor(color_hsv, cv2.COLOR_HSV2BGR)[0][0]
            output[labels == label] = color_bgr

        return output

    def convex_hull(self):
        if self.img_cv is None:
            return None
        img = self._to_binary(self.img_cv)
        contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        result = np.zeros_like(img)
        for contour in contours:
            hull = cv2.convexHull(contour)
            cv2.drawContours(result, [hull], -1, 255, thickness=cv2.FILLED)

        return result

    def thinning(self):
        img = self._to_binary(self.img_cv)
        skeleton = np.zeros_like(img)
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

        while True:
            eroded = cv2.erode(img, kernel)
            temp = cv2.dilate(eroded, kernel)
            temp = cv2.subtract(img, temp)

            skeleton = cv2.bitwise_or(skeleton, temp)
            img = eroded.copy()
            if cv2.countNonZero(img) == 0: break
        return skeleton

    def thickening(self, iterations=3):
        img = self._to_binary(self.img_cv)
        if img is None:
            return None

        iterations = max(1, int(round(iterations)))
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

        return cv2.dilate(img, kernel, iterations=iterations)