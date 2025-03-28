import cv2
import numpy as np
import math


class ZoomManager:
    def __init__(self):
        self.start_distance = None
        self.scale = 1.0
        self.smooth_scale = 1.0

    def reset(self):
        self.start_distance = None

    def adjust(self, img, hands_data):
        try:
            h, w = img.shape[:2]

            if len(hands_data) == 2:
                # Points des index
                hand1 = hands_data[0]["lmList"][8]
                hand2 = hands_data[1]["lmList"][8]
                x1, y1 = hand1["x"], hand1["y"]
                x2, y2 = hand2["x"], hand2["y"]

                # Calcul distance
                current_distance = math.hypot(x2 - x1, y2 - y1)

                if self.start_distance is None:
                    self.start_distance = current_distance

                # Calcul échelle
                self.scale = np.clip(current_distance / self.start_distance, 0.5, 3.0)
                self.smooth_scale = 0.3 * self.smooth_scale + 0.7 * self.scale

                # Application zoom
                M = cv2.getRotationMatrix2D((w // 2, h // 2), 0, self.smooth_scale)
                img = cv2.warpAffine(img, M, (w, h))

                # Affichage
                cv2.putText(img, f"ZOOM: x{self.smooth_scale:.1f}",
                            (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            return img

        except Exception as e:
            print(f"Erreur zoom: {str(e)}")
            self.reset()
            return img