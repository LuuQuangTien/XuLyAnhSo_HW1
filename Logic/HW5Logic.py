import cv2
import numpy as np
import math


class HW5Logic:
    """
    HW5 – Image Segmentation & Auto-Thresholding

    Features:
    1. Moving object segmentation from video (static camera)
    2. Optimal threshold derivation for two Gaussian distributions N(μ1,σ), N(μ2,σ)
    3. Auto-thresholding for object segmentation with counting & lighting
    """

    # ──────────────────────────────────────────────
    # 1. VIDEO MOVING OBJECT SEGMENTATION
    # ──────────────────────────────────────────────

    def video_segment_init(self, video_path, method="MOG2"):
        """Initialize video segmentation.
        video_path: file path string, or 0 for camera.
        Returns (success, cap, subtractor, total_frames).
        """
        if video_path is None:
            return False, None, None, 0

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return False, None, None, 0

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if video_path != 0 else -1

        subtractor = None
        if method == "MOG2":
            subtractor = cv2.createBackgroundSubtractorMOG2(
                history=500, varThreshold=50, detectShadows=True
            )
        elif method == "KNN":
            subtractor = cv2.createBackgroundSubtractorKNN(
                history=500, dist2Threshold=400.0, detectShadows=True
            )
        # "Frame Diff" → subtractor stays None, handled manually

        return True, cap, subtractor, total_frames

    def video_segment_next_frame(self, cap, subtractor, method="MOG2",
                                  prev_frame=None, show_bbox=True, show_thresh=False):
        """Process the next frame from the video.
        show_bbox: draw bounding boxes and object count
        show_thresh: display the foreground mask instead of the original frame
        Returns (success, result_img, fg_mask, current_gray_frame).
        """
        ret, frame = cap.read()
        if not ret or frame is None:
            return False, None, None, None

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        if method == "Frame Diff":
            if prev_frame is None:
                return True, frame, np.zeros_like(gray), gray
            diff = cv2.absdiff(prev_frame, gray)
            _, fg_mask = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
        else:
            fg_mask = subtractor.apply(frame)
            # Remove shadow pixels (value 127 in MOG2/KNN)
            _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

        # Morphological cleanup
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel, iterations=1)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel, iterations=2)

        # Choose display mode
        if show_thresh:
            result = cv2.cvtColor(fg_mask, cv2.COLOR_GRAY2BGR)
        else:
            result = frame.copy()
            # Green tint on moving regions
            overlay = result.copy()
            overlay[fg_mask > 0] = [0, 200, 0]
            cv2.addWeighted(overlay, 0.3, result, 0.7, 0, result)

        # Bounding boxes
        if show_bbox:
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            obj_count = 0
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > 500:
                    obj_count += 1
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(result, f"{obj_count}", (x + 2, y - 6),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(result, f"Method: {method} | Objects: {obj_count}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        else:
            cv2.putText(result, f"Method: {method}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        return True, result, fg_mask, gray

    # ──────────────────────────────────────────────
    # 2. OPTIMAL GAUSSIAN THRESHOLD (σ chung)
    # ──────────────────────────────────────────────

    def compute_optimal_threshold(self, mu1, mu2, sigma, p):
        """
        Compute optimal threshold T that minimizes classification error
        for two Gaussian distributions with EQUAL variance:

            Background: N(μ₁, σ) with proportion (1 - p)
            Object:     N(μ₂, σ) with proportion p

        Formula:
            T = (μ₁ + μ₂) / 2 + σ² · ln((1-p)/p) / (μ₂ - μ₁)

        When p = 0.5: T = (μ₁ + μ₂) / 2  (midpoint)
        """
        if abs(mu2 - mu1) < 1e-6:
            return (mu1 + mu2) / 2.0

        sigma = max(sigma, 1e-6)
        p = max(0.01, min(0.99, p))

        T = (mu1 + mu2) / 2.0 + (sigma ** 2) * math.log((1 - p) / p) / (mu2 - mu1)
        return T

    def plot_gaussian_threshold(self, mu1, mu2, sigma, p):
        """
        Generate a visualization of two Gaussian distributions with the
        optimal threshold line, error regions, and the derivation formula.
        Returns (cv2_image_bgr, threshold_value).
        """
        sigma = max(sigma, 1e-6)
        threshold = self.compute_optimal_threshold(mu1, mu2, sigma, p)

        # Build x-axis range
        x_min = min(mu1 - 4 * sigma, mu2 - 4 * sigma, 0)
        x_max = max(mu1 + 4 * sigma, mu2 + 4 * sigma, 255)
        x = np.linspace(x_min, x_max, 1000)

        # Gaussian PDFs
        def gauss(x_arr, mu, s):
            return np.exp(-0.5 * ((x_arr - mu) / s) ** 2) / (s * np.sqrt(2 * np.pi))

        y1 = (1 - p) * gauss(x, mu1, sigma)
        y2 = p * gauss(x, mu2, sigma)

        # Render using OpenCV drawing
        img_w, img_h = 800, 520
        margin_l, margin_r, margin_t, margin_b = 80, 40, 60, 80
        plot_w = img_w - margin_l - margin_r
        plot_h = img_h - margin_t - margin_b

        img = np.full((img_h, img_w, 3), 30, dtype=np.uint8)

        y_max_val = max(np.max(y1), np.max(y2)) * 1.15
        if y_max_val < 1e-10:
            y_max_val = 1.0

        def to_px(xv, yv):
            px = int(margin_l + (xv - x_min) / (x_max - x_min) * plot_w)
            py = int(margin_t + plot_h - yv / y_max_val * plot_h)
            return (px, py)

        # Draw grid
        for i in range(5):
            gy = margin_t + int(plot_h * i / 4)
            cv2.line(img, (margin_l, gy), (img_w - margin_r, gy), (50, 50, 50), 1)
            val = y_max_val * (4 - i) / 4
            cv2.putText(img, f"{val:.4f}", (5, gy + 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (150, 150, 150), 1)

        n_ticks = 6
        for i in range(n_ticks + 1):
            gx = margin_l + int(plot_w * i / n_ticks)
            cv2.line(img, (gx, margin_t), (gx, margin_t + plot_h), (50, 50, 50), 1)
            val = x_min + (x_max - x_min) * i / n_ticks
            cv2.putText(img, f"{val:.0f}", (gx - 12, margin_t + plot_h + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)

        # Axes
        cv2.line(img, (margin_l, margin_t), (margin_l, margin_t + plot_h), (200, 200, 200), 1)
        cv2.line(img, (margin_l, margin_t + plot_h), (img_w - margin_r, margin_t + plot_h), (200, 200, 200), 1)

        # Error regions (shaded)
        for i in range(len(x) - 1):
            xi = x[i]
            if xi > threshold:
                px1 = to_px(x[i], 0)
                px2 = to_px(x[i], y1[i])
                if px2[1] < px1[1]:
                    cv2.line(img, (px1[0], px1[1]), (px2[0], px2[1]), (60, 60, 140), 1)
            else:
                px1 = to_px(x[i], 0)
                px2 = to_px(x[i], y2[i])
                if px2[1] < px1[1]:
                    cv2.line(img, (px1[0], px1[1]), (px2[0], px2[1]), (140, 60, 60), 1)

        # Draw curves
        pts1 = [to_px(x[i], y1[i]) for i in range(len(x))]
        pts2 = [to_px(x[i], y2[i]) for i in range(len(x))]

        for i in range(len(pts1) - 1):
            cv2.line(img, pts1[i], pts1[i + 1], (255, 200, 100), 2)  # Background: orange-ish
        for i in range(len(pts2) - 1):
            cv2.line(img, pts2[i], pts2[i + 1], (100, 255, 100), 2)  # Object: green

        # Threshold line
        tx = to_px(threshold, 0)[0]
        cv2.line(img, (tx, margin_t), (tx, margin_t + plot_h), (0, 0, 255), 2)
        cv2.putText(img, f"T = {threshold:.1f}", (tx + 5, margin_t + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 100, 255), 2)

        # Mu markers
        mx1 = to_px(mu1, 0)[0]
        mx2 = to_px(mu2, 0)[0]
        cv2.drawMarker(img, (mx1, margin_t + plot_h + 8), (255, 200, 100),
                       cv2.MARKER_TRIANGLE_UP, 10, 2)
        cv2.putText(img, f"mu1={mu1:.0f}", (mx1 - 20, margin_t + plot_h + 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 200, 100), 1)
        cv2.drawMarker(img, (mx2, margin_t + plot_h + 8), (100, 255, 100),
                       cv2.MARKER_TRIANGLE_UP, 10, 2)
        cv2.putText(img, f"mu2={mu2:.0f}", (mx2 - 20, margin_t + plot_h + 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 255, 100), 1)

        # Title
        cv2.putText(img, "Optimal Gaussian Threshold (Equal Variance)", (img_w // 2 - 220, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 240, 240), 2)

        # Legend
        cv2.line(img, (img_w - 250, 15), (img_w - 230, 15), (255, 200, 100), 2)
        cv2.putText(img, f"BG: N({mu1:.0f}, {sigma:.0f}), w = {1 - p:.0%}", (img_w - 225, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 200, 100), 1)
        cv2.line(img, (img_w - 250, 35), (img_w - 230, 35), (100, 255, 100), 2)
        cv2.putText(img, f"OBJ: N({mu2:.0f}, {sigma:.0f}), w = {p:.0%}", (img_w - 225, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 255, 100), 1)

        # Formula at bottom
        formula1 = f"T = (mu1 + mu2)/2 + sigma^2 * ln((1-p)/p) / (mu2 - mu1)"
        formula2 = f"T = ({mu1:.0f}+{mu2:.0f})/2 + {sigma:.0f}^2 * ln(({1-p:.2f})/{p:.2f}) / ({mu2:.0f}-{mu1:.0f}) = {threshold:.2f}"
        cv2.putText(img, formula1, (margin_l, img_h - 38),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180, 220, 255), 1)
        cv2.putText(img, formula2, (margin_l, img_h - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 200), 1)

        return img, threshold

    # ──────────────────────────────────────────────
    # 3. AUTO-THRESHOLDING & OBJECT COUNTING
    # ──────────────────────────────────────────────

    def _estimate_gaussian_params(self, gray_img):
        """
        Estimate parameters of two Gaussian distributions from image histogram.
        Uses Otsu's threshold as initial split, then computes mean/std for each class.
        Returns (mu1, mu2, sigma, p) where sigma is the pooled std.
        """
        hist = cv2.calcHist([gray_img], [0], None, [256], [0, 256]).flatten()
        total = hist.sum()

        # Otsu split to estimate initial two classes
        thresh_otsu, _ = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        thresh_otsu = int(thresh_otsu)

        # Class 1 (background): pixels <= thresh_otsu
        w1 = hist[:thresh_otsu + 1].sum()
        if w1 > 0:
            vals1 = np.arange(thresh_otsu + 1)
            mu1 = np.sum(vals1 * hist[:thresh_otsu + 1]) / w1
            var1 = np.sum(((vals1 - mu1) ** 2) * hist[:thresh_otsu + 1]) / w1
        else:
            mu1, var1 = 0, 1

        # Class 2 (object): pixels > thresh_otsu
        w2 = hist[thresh_otsu + 1:].sum()
        if w2 > 0:
            vals2 = np.arange(thresh_otsu + 1, 256)
            mu2 = np.sum(vals2 * hist[thresh_otsu + 1:]) / w2
            var2 = np.sum(((vals2 - mu2) ** 2) * hist[thresh_otsu + 1:]) / w2
        else:
            mu2, var2 = 255, 1

        # Pooled standard deviation (equal variance assumption)
        if total > 0:
            sigma = math.sqrt((w1 * var1 + w2 * var2) / total)
        else:
            sigma = 1.0
        sigma = max(sigma, 1.0)

        p = w2 / total if total > 0 else 0.5

        return mu1, mu2, sigma, p

    def auto_threshold_segment(self):
        """
        Segment objects from image using the optimal Gaussian threshold formula.
        Estimates distribution parameters from the histogram, computes T, and applies.
        Returns (binary_img, threshold_value, mu1, mu2, sigma, p).
        """
        if self.img_cv is None:
            return None, 0, 0, 0, 0, 0

        gray = self.img_cv
        if len(gray.shape) == 3:
            gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)

        mu1, mu2, sigma, p = self._estimate_gaussian_params(gray)
        T = self.compute_optimal_threshold(mu1, mu2, sigma, p)
        T_int = int(np.clip(round(T), 0, 255))

        _, binary = cv2.threshold(gray, T_int, 255, cv2.THRESH_BINARY)

        return binary, T, mu1, mu2, sigma, p

    def count_objects(self, binary_img, min_area=100):
        """
        Count objects in a binary image using contour detection.
        Returns (annotated_image_bgr, object_count).
        """
        if binary_img is None:
            return None, 0

        if len(binary_img.shape) == 3:
            binary_img = cv2.cvtColor(binary_img, cv2.COLOR_BGR2GRAY)

        # Clean up noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        cleaned = cv2.morphologyEx(binary_img, cv2.MORPH_OPEN, kernel, iterations=1)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel, iterations=1)

        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        output = cv2.cvtColor(binary_img, cv2.COLOR_GRAY2BGR)

        obj_count = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < min_area:
                continue
            obj_count += 1
            x, y, w, h = cv2.boundingRect(cnt)
            hue = int(180 * obj_count / max(len(contours), 1))
            color_hsv = np.uint8([[[hue, 220, 240]]])
            color_bgr = cv2.cvtColor(color_hsv, cv2.COLOR_HSV2BGR)[0][0]
            color = tuple(int(c) for c in color_bgr)

            cv2.rectangle(output, (x, y), (x + w, y + h), color, 2)
            cv2.putText(output, f"{obj_count}", (x + 2, y - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        cv2.putText(output, f"Objects: {obj_count} (min_area={min_area})",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        return output, obj_count

    # ──────────────────────────────────────────────
    # LIGHTING DIRECTION SIMULATION
    # ──────────────────────────────────────────────

    def apply_lighting_direction(self, angle_deg=0, intensity=0.5):
        """
        Simulate directional lighting by creating a gradient overlay.
        angle_deg: direction of light source (0=right, 90=top, 180=left, 270=bottom)
        intensity: strength of lighting effect (0.0 to 1.0)
        Returns the lit image.
        """
        if self.img_cv is None:
            return None

        img = self.img_cv.copy()
        h, w = img.shape[:2]

        angle_rad = math.radians(angle_deg)
        dx = math.cos(angle_rad)
        dy = -math.sin(angle_rad)

        y_coords, x_coords = np.mgrid[0:h, 0:w]
        x_norm = (x_coords / max(w - 1, 1)) * 2 - 1
        y_norm = (y_coords / max(h - 1, 1)) * 2 - 1

        gradient = (x_norm * dx + y_norm * dy)
        gradient = (gradient - gradient.min()) / (gradient.max() - gradient.min() + 1e-8)

        light_factor = (1 - intensity) + 2 * intensity * gradient
        light_factor = light_factor.astype(np.float32)

        if len(img.shape) == 3:
            light_factor = np.stack([light_factor] * 3, axis=-1)

        result = np.clip(img.astype(np.float32) * light_factor, 0, 255).astype(np.uint8)
        return result

    def segment_count_objects(self, angle_deg=0, intensity=0.0, min_area=100):
        """
        Full pipeline: optionally apply lighting, then auto-threshold using optimal
        Gaussian formula, then count objects.
        Returns (annotated_image, count, threshold, mu1, mu2, sigma, p).
        """
        if self.img_cv is None:
            return None, 0, 0, 0, 0, 0, 0

        # Apply lighting if intensity > 0
        if intensity > 0.01:
            lit = self.apply_lighting_direction(angle_deg, intensity)
            original = self.img_cv
            self.img_cv = lit
            binary, T, mu1, mu2, sigma, p = self.auto_threshold_segment()
            self.img_cv = original
        else:
            binary, T, mu1, mu2, sigma, p = self.auto_threshold_segment()

        if binary is None:
            return None, 0, 0, 0, 0, 0, 0

        annotated, count = self.count_objects(binary, min_area=min_area)
        return annotated, count, T, mu1, mu2, sigma, p
