from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import numpy as np
import cv2
import math


class VolumeController:
    def __init__(self):
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = self.interface.QueryInterface(IAudioEndpointVolume)
        self.vol_range = self.volume.GetVolumeRange()
        self.min_vol, self.max_vol = self.vol_range[0], self.vol_range[1]

    def adjust(self, img, thumb, index):
        try:
            # Calcul distance relative
            x1, y1 = thumb["x"], thumb["y"]
            x2, y2 = index["x"], index["y"]
            length = math.hypot(x2 - x1, y2 - y1)

            # Conversion en volume
            vol = np.interp(length, [50, 300], [self.min_vol, self.max_vol])
            self.volume.SetMasterVolumeLevel(vol, None)

            # Affichage
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
            vol_percent = int(np.interp(length, [50, 300], [0, 100]))
            cv2.putText(img, f'VOL: {vol_percent}%', (x2 + 20, y2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        except Exception as e:
            print(f"Erreur volume: {str(e)}")

        return img