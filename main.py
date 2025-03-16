import cv2
import time
from utils.hand_tracking import HandDetector
from utils.volume_control import VolumeController
from utils.screenshot import ScreenshotTaker
from utils.zoom_control import ZoomManager
import winsound  # Feedback sonore


def main():
    # Configuration
    wCam, hCam = 1280, 720
    SCREENSHOT_CONFIDENCE = 0.3
    GESTURE_HISTORY = []
    GESTURE_HISTORY_LENGTH = 15
    cooldown_frames = 0  # Nouveau : empêche les changements trop rapides

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

        img = detector.find_hands(img)
        hands_data = detector.get_landmarks(img)

        # Affichage FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (40, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

        try:
            if mode == "menu":
                # Affichage du menu
                cv2.putText(img, "MENU :", (40, 120), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 3)
                cv2.putText(img, "1. Index leve - Volume", (40, 180), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 2)
                cv2.putText(img, "2. 3 Doigts - Capture", (40, 240), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 2)
                cv2.putText(img, "3. 2 Mains - Zoom", (40, 300), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 2)

                if hands_data and cooldown_frames == 0:
                    fingers = detector.fingers_up(hands_data[0], SCREENSHOT_CONFIDENCE)

                    # Détection Volume
                    if fingers == [0, 1, 0, 0, 0]:
                        mode = "volume"
                        cooldown_frames = 15  # Ajout du cooldown

                    # Détection Screenshot
                    elif sum(fingers) == 3:
                        mode = "screenshot"
                        screenshot_cooldown = 30
                        GESTURE_HISTORY = []
                        cooldown_frames = 15  # Ajout du cooldown

                    # Détection Zoom (2 mains)
                    elif len(hands_data) == 2:
                        mode = "zoom"
                        zoom.reset()
                        cooldown_frames = 15  # Ajout du cooldown

            elif mode == "volume":
                if hands_data and len(hands_data[0]["lmList"]) >= 21:
                    hand = hands_data[0]
                    img = vol_control.adjust(img, hand["lmList"][4], hand["lmList"][8])

                    # Retour au menu si la main s'ouvre complètement
                    if detector.fingers_up(hand) == [1, 1, 1, 1, 1]:
                        mode = "menu"
                        cooldown_frames = 15  # Ajout du cooldown

            elif mode == "screenshot":
                if screenshot_cooldown > 0:
                    if hands_data:
                        current_fingers = detector.fingers_up(hands_data[0], 0.35)

                        # Vérification des 3 doigts levés dans l'historique
                        GESTURE_HISTORY.append(sum(current_fingers) >= 3)

                        if len(GESTURE_HISTORY) > GESTURE_HISTORY_LENGTH:
                            GESTURE_HISTORY.pop(0)

                        confidence_level = sum(GESTURE_HISTORY) / len(GESTURE_HISTORY) if GESTURE_HISTORY else 0
                        cv2.rectangle(img, (0, 0), (int(wCam * confidence_level), 30), (0, 255, 0), -1)

                        # Si le geste est stable, capture
                        if confidence_level >= 0.6 and screenshot_cooldown == 30:
                            if screenshot.capture():
                                winsound.Beep(1000, 200)  # Feedback sonore
                                cv2.putText(img, "CAPTURE REUSSIE!", (wCam // 2 - 300, hCam // 2),
                                            cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 3)
                                cv2.imshow("Gesture Control", img)
                                cv2.waitKey(500)
                                screenshot_cooldown = 29

                    screenshot_cooldown -= 1
                else:
                    mode = "menu"
                    GESTURE_HISTORY = []
                    cooldown_frames = 15  # Ajout du cooldown

            elif mode == "zoom":
                if len(hands_data) == 2:
                    img = zoom.adjust(img, hands_data)
                else:
                    mode = "menu"
                    zoom.reset()
                    cooldown_frames = 15  # Ajout du cooldown

        except Exception as e:
            print(f"Erreur: {str(e)}")
            mode = "menu"

        # Décompte du cooldown
        if cooldown_frames > 0:
            cooldown_frames -= 1

        cv2.imshow("Gesture Control", img)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
