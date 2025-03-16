import cv2
import time
from utils.hand_tracking import HandDetector
from utils.volume_control import VolumeController
from utils.screenshot import ScreenshotTaker
from utils.zoom_control import ZoomManager


def main():
    # Configuration
    wCam, hCam = 1280, 720

    # Initialisation
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)

    detector = HandDetector()
    vol_control = VolumeController()
    screenshot = ScreenshotTaker()
    zoom = ZoomManager()

    pTime = 0
    mode = "menu"
    screenshot_cooldown = 0

    while True:
        success, img = cap.read()
        if not success:
            continue

        # Détection des mains
        img = detector.find_hands(img)
        hands_data = detector.get_landmarks(img)

        # FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (40, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

        # Gestion des modes
        try:
            if mode == "menu":
                cv2.putText(img, "MENU :", (40, 120), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 3)
                cv2.putText(img, "1. Index leve - Volume", (40, 180), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 2)
                cv2.putText(img, "2. 3 Doigts - Capture", (40, 240), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 2)
                cv2.putText(img, "3. 2 Mains - Zoom", (40, 300), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 2)

                if hands_data:
                    fingers = detector.fingers_up(hands_data[0])

                    # Activation volume
                    if fingers == [0, 1, 0, 0, 0]:
                        mode = "volume"
                        print("VOLUME ACTIVE")

                    # Activation capture
                    elif fingers[:3] == [1, 1, 1]:
                        mode = "screenshot"
                        screenshot_cooldown = 30

                    # Activation zoom
                    if len(hands_data) == 2:
                        mode = "zoom"
                        zoom.reset()

            elif mode == "volume":
                if hands_data and len(hands_data) >= 1:
                    hand = hands_data[0]
                    if len(hand["lmList"]) >= 21:
                        thumb = hand["lmList"][4]
                        index = hand["lmList"][8]
                        img = vol_control.adjust(img, thumb, index)

                        # Vérification index baissé
                        if hand["lmList"][8]["y"] > hand["lmList"][6]["y"]:
                            mode = "menu"

            elif mode == "screenshot":
                if screenshot_cooldown > 0:
                    if screenshot_cooldown == 30:
                        screenshot.capture()
                        cv2.putText(img, "CAPTURE EFFECTUEE!", (300, 300),
                                    cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 3)
                    screenshot_cooldown -= 1
                else:
                    mode = "menu"

            elif mode == "zoom":
                if len(hands_data) == 2:
                    img = zoom.adjust(img, hands_data)
                else:
                    mode = "menu"
                    zoom.reset()

        except Exception as e:
            print(f"Erreur générale: {str(e)}")
            mode = "menu"

        cv2.imshow("Gesture Control", img)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()