import cv2
import numpy as np
import math

class ZoomManager:
    def __init__(self):
        self.start_distance = None
        self.scale = 1.0
        self.base_image = None
        self.offset_x = 0
        self.offset_y = 0
        self.pan_start = None

    def capture_base_image(self, img):
        """Capture the base image and reset zoom parameters."""
        self.base_image = img.copy()
        self.offset_x = 0
        self.offset_y = 0
        self.scale = 1.0

    def adjust(self, hands_data):
        """Adjust the zoom based on hand movement."""
        try:
            if len(hands_data) == 2 and self.base_image is not None:
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

                # Calcul centre du zoom
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)

                # Application zoom avec translation
                h, w = self.base_image.shape[:2]
                M = cv2.getRotationMatrix2D((center_x, center_y), 0, self.scale)
                M[0, 2] += self.offset_x
                M[1, 2] += self.offset_y
                zoomed_img = cv2.warpAffine(self.base_image, M, (w, h))

                # Ajout HUD
                cv2.putText(zoomed_img, f"ZOOM: x{self.scale:.1f}", (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                cv2.rectangle(zoomed_img, (center_x - 10, center_y - 10),
                              (center_x + 10, center_y + 10), (0, 255, 0), 2)

                return zoomed_img

            return self.base_image

        except Exception as e:
            print(f"Erreur zoom: {str(e)}")
            return self.base_image if self.base_image is not None else np.zeros((480, 640, 3), dtype=np.uint8)

    def reset(self):
        """Reset the zoom parameters to their default state."""
        self.start_distance = None
        self.scale = 1.0
        self.base_image = None
        self.offset_x = 0
        self.offset_y = 0
        self.pan_start = None
