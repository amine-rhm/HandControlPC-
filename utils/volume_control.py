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
            if not thumb or not index:
                return img

            # Conversion des coordonnées
            x1, y1 = thumb['x'], thumb['y']
            x2, y2 = index['x'], index['y']

            # Calcul de la distance
            length = math.hypot(x2 - x1, y2 - y1)
            vol = np.interp(length, [30, 250], [self.min_vol, self.max_vol])
            self.volume.SetMasterVolumeLevel(vol, None)

            # Affichage
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
            vol_percent = int(np.interp(vol, [self.min_vol, self.max_vol], [0, 100]))
            cv2.putText(img, f'VOL: {vol_percent}%', (40, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        except Exception as e:
            print(f"Erreur volume: {str(e)}")

        return img