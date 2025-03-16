import cv2
import numpy as np
import math


class ZoomManager:
    def __init__(self):
        self.start_distance = None
        self.base_scale = 1.0
        self.scale = 1.0
        self.smooth_scale = 1.0

    def reset(self):
        self.start_distance = None
        self.base_scale = 1.0

    def adjust(self, img, hands_data):
        try:
            h, w = img.shape[:2]

            if len(hands_data) >= 2:
                # Vérification des données
                hand1 = hands_data[0].get('lmList', [])
                hand2 = hands_data[1].get('lmList', [])

                if len(hand1) < 9 or len(hand2) < 9:
                    raise ValueError("Landmarks manquants")

                # Points des index
                x1, y1 = hand1[8]['x'], hand1[8]['y']
                x2, y2 = hand2[8]['x'], hand2[8]['y']

                # Calcul de distance
                current_distance = math.hypot(x2 - x1, y2 - y1)

                if self.start_distance is None:
                    self.start_distance = current_distance
                    self.base_scale = self.scale

                # Calcul du zoom
                scale_factor = current_distance / self.start_distance
                self.scale = np.clip(self.base_scale * scale_factor, 0.5, 3.0)
                self.smooth_scale = 0.3 * self.smooth_scale + 0.7 * self.scale

                # Application du zoom
                M = cv2.getRotationMatrix2D((w // 2, h // 2), 0, self.smooth_scale)
                return cv2.warpAffine(img, M, (w, h))

            return img

        except Exception as e:
            print(f"Erreur zoom: {str(e)}")
            self.reset()
            return img