import os
import time
import mss

class ScreenshotTaker:
    def __init__(self):
        self.folder = "screenshots"
        os.makedirs(self.folder, exist_ok=True)
        print(f"Dossier '{self.folder}' prêt.")

        # Test initial des permissions
        self.test_capture()

    def test_capture(self):
        try:
            test_file = os.path.join(self.folder, "test_capture.png")
            with mss.mss() as sct:
                sct.shot(output=test_file)

            if os.path.exists(test_file):
                os.remove(test_file)
                print("Test de capture réussi!")
            else:
                print("Erreur lors du test de capture")
        except Exception as e:
            print(f"ERREUR PERMISSIONS: {str(e)}")

    def capture(self):
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.folder, f"capture_{timestamp}.png")

            with mss.mss() as sct:
                sct.shot(output=filename)

            if os.path.exists(filename):
                print(f"Capture sauvegardée: {filename}")
                return True
            return False

        except Exception as e:
            print(f"ERREUR CAPTURE: {str(e)}")
            return False


# Test de la classe
if __name__ == "__main__":
    taker = ScreenshotTaker()
    taker.capture()
