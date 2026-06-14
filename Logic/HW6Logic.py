import os
import cv2
import numpy as np

class HW6Logic:
    def init_hw6(self):
        self._project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._dataset_dir = os.path.join(self._project_root, "dataset")
        self._model_dir = os.path.join(self._project_root, "models")
        self._model_path = os.path.join(self._model_dir, "face_model.npz")
        
        # Ensure directories exist
        os.makedirs(self._dataset_dir, exist_ok=True)
        os.makedirs(self._model_dir, exist_ok=True)
        
        # Load Haar Cascade
        self._face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Model variables
        self.mean_face = None
        self.eigenfaces = None  # shape (K, 4096)
        self.weights = None     # shape (N, K)
        self.labels = None      # shape (N,)
        self.label_names = []   # list of profile name strings
        self.is_trained = False
        
        self.load_face_model()

    def get_dataset_dir(self):
        if not hasattr(self, "_dataset_dir"):
            self.init_hw6()
        return self._dataset_dir

    def get_profiles(self):
        dataset_dir = self.get_dataset_dir()
        if not os.path.exists(dataset_dir):
            return []
        profiles = []
        for name in os.listdir(dataset_dir):
            p_path = os.path.join(dataset_dir, name)
            if os.path.isdir(p_path):
                # Count files inside
                files = [f for f in os.listdir(p_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                profiles.append((name, len(files)))
        return sorted(profiles)

    def detect_faces(self, cv_img):
        if not hasattr(self, "_face_cascade"):
            self.init_hw6()
        
        if cv_img is None:
            return []
        
        if len(cv_img.shape) == 3:
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = cv_img
            
        # Detect faces
        faces = self._face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(40, 40)
        )
        return faces

    def save_face_sample(self, frame, bbox, label_name, count):
        dataset_dir = self.get_dataset_dir()
        label_dir = os.path.join(dataset_dir, label_name)
        os.makedirs(label_dir, exist_ok=True)
        
        x, y, w, h = bbox
        # Add a small padding around face
        h_img, w_img = frame.shape[:2]
        pad_x = int(w * 0.1)
        pad_y = int(h * 0.1)
        
        x1 = max(0, x - pad_x)
        y1 = max(0, y - pad_y)
        x2 = min(w_img, x + w + pad_x)
        y2 = min(h_img, y + h + pad_y)
        
        face_crop = frame[y1:y2, x1:x2]
        if face_crop.size == 0:
            return False
            
        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY) if len(face_crop.shape) == 3 else face_crop
        resized = cv2.resize(gray, (64, 64))
        
        file_path = os.path.join(label_dir, f"face_{count:03d}.jpg")
        cv2.imwrite(file_path, resized)
        return True

    def train_face_classifier(self):
        if not hasattr(self, "_dataset_dir"):
            self.init_hw6()
            
        profiles = self.get_profiles()
        if not profiles:
            return False, "Dataset is empty. Capture face samples first."
            
        X_list = []
        y_list = []
        label_names = []
        
        for idx, (name, count) in enumerate(profiles):
            if count == 0:
                continue
            label_names.append(name)
            class_id = len(label_names) - 1
            
            label_dir = os.path.join(self._dataset_dir, name)
            for f in os.listdir(label_dir):
                if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(label_dir, f)
                    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    if img is None:
                        continue
                    # Resize just in case
                    if img.shape != (64, 64):
                        img = cv2.resize(img, (64, 64))
                    
                    # Normalize to [0.0, 1.0] and flatten
                    vector = img.astype(np.float32) / 255.0
                    X_list.append(vector.flatten())
                    y_list.append(class_id)
                    
        if not X_list:
            return False, "No valid images found in dataset."
            
        X = np.array(X_list)  # (N, 4096)
        y = np.array(y_list)  # (N,)
        N, D = X.shape
        mean_face = np.mean(X, axis=0)
        A = X - mean_face  # (N, 4096)
        K = min(N, 30)
        if N > 1:
            K = min(N - 1, 30)
        K = max(1, K)
        
        if N == 1:
            # Single sample PCA fallback
            eigenvectors_selected = np.zeros((D, 1), dtype=np.float32)
            eigenvectors_selected[:, 0] = A[0] / (np.linalg.norm(A[0]) + 1e-8)
            weights = A @ eigenvectors_selected
        else:
            L = A @ A.T
            eigenvalues, U = np.linalg.eigh(L)
            sort_idx = np.argsort(eigenvalues)[::-1]
            eigenvalues = eigenvalues[sort_idx]
            U = U[:, sort_idx]
            eigenvectors = A.T @ U  # (4096, N)

            norms = np.linalg.norm(eigenvectors, axis=0)
            norms[norms == 0] = 1.0
            eigenvectors = eigenvectors / norms
            eigenvectors_selected = eigenvectors[:, :K]  # (4096, K)
            weights = A @ eigenvectors_selected  # (N, K)
            
        self.mean_face = mean_face
        self.eigenfaces = eigenvectors_selected.T  # (K, 4096)
        self.weights = weights
        self.labels = y
        self.label_names = label_names
        self.is_trained = True
        
        self.save_face_model()
        return True, f"Model trained successfully on {N} samples across {len(profiles)} profiles."

    def save_face_model(self):
        if not self.is_trained:
            return
        try:
            os.makedirs(self._model_dir, exist_ok=True)
            np.savez_compressed(
                self._model_path,
                mean_face=self.mean_face,
                eigenfaces=self.eigenfaces,
                weights=self.weights,
                labels=self.labels,
                label_names=np.array(self.label_names)
            )
        except Exception:
            pass

    def load_face_model(self):
        if not hasattr(self, "_model_path"):
            self.init_hw6()
        if os.path.exists(self._model_path):
            try:
                data = np.load(self._model_path, allow_pickle=True)
                self.mean_face = data['mean_face']
                self.eigenfaces = data['eigenfaces']
                self.weights = data['weights']
                self.labels = data['labels']
                self.label_names = list(data['label_names'])
                self.is_trained = True
                return True
            except Exception:
                self.is_trained = False
        return False

    def clear_dataset(self):
        import shutil
        dataset_dir = self.get_dataset_dir()
        if os.path.exists(dataset_dir):
            shutil.rmtree(dataset_dir)
        os.makedirs(dataset_dir, exist_ok=True)
        
        model_path = getattr(self, "_model_path", None)
        if model_path and os.path.exists(model_path):
            try:
                os.remove(model_path)
            except Exception:
                pass
                
        self.mean_face = None
        self.eigenfaces = None
        self.weights = None
        self.labels = None
        self.label_names = []
        self.is_trained = False

    def recognize_face(self, face_img, threshold=12.0):
        if not self.is_trained or self.mean_face is None:
            return "Unknown", 0.0
            
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY) if len(face_img.shape) == 3 else face_img
        resized = cv2.resize(gray, (64, 64))

        q = (resized.astype(np.float32) / 255.0).flatten()
        q_diff = q - self.mean_face

        w_q = q_diff @ self.eigenfaces.T  # (K,)

        distances = np.linalg.norm(self.weights - w_q, axis=1)
        min_idx = np.argmin(distances)
        min_dist = distances[min_idx]
        
        if min_dist <= threshold:
            predicted_label = self.labels[min_idx]
            name = self.label_names[predicted_label]
            confidence = max(0.0, 100.0 * (1.0 - (min_dist / threshold)))
            return name, confidence
        else:
            return "Unknown", 0.0

    def get_eigenfaces_visualization(self):
        if not self.is_trained or self.mean_face is None:
            return None

        def to_img(v):
            img = v.reshape(64, 64)
            # Normalize to 0-255
            v_min, v_max = img.min(), img.max()
            if v_max - v_min > 1e-5:
                img_norm = (img - v_min) / (v_max - v_min) * 255
            else:
                img_norm = np.zeros_like(img)
            return img_norm.astype(np.uint8)
            
        mean_img = to_img(self.mean_face)
        
        images = [mean_img]
        num_eigen = min(4, self.eigenfaces.shape[0])
        for i in range(num_eigen):
            images.append(to_img(self.eigenfaces[i]))

        while len(images) < 5:
            images.append(np.zeros((64, 64), dtype=np.uint8))
        resized_imgs = [cv2.resize(img, (120, 120)) for img in images]
        
        # Add borders
        bordered_imgs = []
        for idx, img in enumerate(resized_imgs):
            bordered = cv2.copyMakeBorder(img, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=100)
            bordered_imgs.append(bordered)
            
        # Combine side-by-side
        combined = np.hstack(bordered_imgs)
        
        # Convert to BGR
        combined_bgr = cv2.cvtColor(combined, cv2.COLOR_GRAY2BGR)
        
        # Add labels text
        cv2.putText(combined_bgr, "Mean Face", (12, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        for i in range(4):
            cv2.putText(combined_bgr, f"Eigenface {i+1}", (120 * (i+1) + 12, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
            
        return combined_bgr
