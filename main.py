import cv2
import time
import numpy as np
from utils.hand_tracking import HandDetector
from utils.volume_control import VolumeController
from utils.screenshot import ScreenshotTaker
from utils.zoom_control import ZoomManager
import winsound

def main():
    # Configuration
    wCam, hCam = 1280, 720
    SCREENSHOT_CONFIDENCE = 0.3
    GESTURE_HISTORY = []
    GESTURE_HISTORY_LENGTH = 15
    cooldown_frames = 0
    CUSTOM_IMAGE_PATH = "utils/logo.png/tester.jpg"

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

        # Calcul du nombre de doigts levés
        total_fingers = 0
        if hands_data:
            for hand in hands_data:
                fingers = detector.fingers_up(hand, SCREENSHOT_CONFIDENCE)
                total_fingers += sum(fingers)

        # Affichage FPS et doigts
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (40, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
        cv2.putText(img, f'Doigts: {total_fingers}', (wCam - 300, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

        try:
            if mode == "menu":
                cv2.putText(img, "MENU :", (40, 120), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 3)
                cv2.putText(img, "1. Index leve - Volume", (40, 180), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 2)
                cv2.putText(img, "2. 3 Doigts - Capture", (40, 240), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 2)
                cv2.putText(img, "3. 2 Mains - Zoom", (40, 300), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 2)

                if hands_data and cooldown_frames == 0:
                    main_hand = hands_data[0]
                    fingers = detector.fingers_up(main_hand, SCREENSHOT_CONFIDENCE)

                    if fingers == [0, 1, 0, 0, 0]:
                        mode = "volume"
                        cooldown_frames = 15

                    elif sum(fingers) == 3:
                        mode = "screenshot"
                        screenshot_cooldown = 30
                        GESTURE_HISTORY = []
                        cooldown_frames = 15

                    elif len(hands_data) == 2:
                        mode = "zoom"
                        zoom.reset()
                        cooldown_frames = 15

            elif mode == "volume":
                if hands_data and len(hands_data[0]["lmList"]) >= 21:
                    hand = hands_data[0]
                    img = vol_control.adjust(img, hand["lmList"][4], hand["lmList"][8])

                    if detector.fingers_up(hand) == [1, 1, 1, 1, 1]:
                        mode = "menu"
                        cooldown_frames = 15

            elif mode == "screenshot":
                if screenshot_cooldown > 0:
                    if hands_data:
                        current_fingers = detector.fingers_up(hands_data[0], 0.35)

                        GESTURE_HISTORY.append(sum(current_fingers) >= 3)

                        if len(GESTURE_HISTORY) > GESTURE_HISTORY_LENGTH:
                            GESTURE_HISTORY.pop(0)

                        confidence_level = sum(GESTURE_HISTORY)/len(GESTURE_HISTORY) if GESTURE_HISTORY else 0
                        cv2.rectangle(img, (0, 0), (int(wCam * confidence_level), 30), (0, 255, 0), -1)

                        if confidence_level >= 0.6 and screenshot_cooldown == 30:
                            if screenshot.capture():
                                winsound.Beep(1000, 200)
                                cv2.putText(img, "CAPTURE REUSSIE!", (wCam//2 - 300, hCam//2),
                                            cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 3)
                                cv2.imshow("Gesture Control", img)
                                cv2.waitKey(500)
                                screenshot_cooldown = 29

                    screenshot_cooldown -= 1
                else:
                    mode = "menu"
                    GESTURE_HISTORY = []
                    cooldown_frames = 15

            elif mode == "zoom":
                if len(hands_data) == 2:
                    if zoom.base_image is None:
                        custom_img = cv2.imread(CUSTOM_IMAGE_PATH)
                        if custom_img is not None:
                            custom_img = cv2.resize(custom_img, (wCam, hCam))
                            zoom.base_image = custom_img
                        else:
                            print(f"Erreur de chargement: {CUSTOM_IMAGE_PATH}")
                            mode = "menu"
                            continue

                    hand1 = hands_data[0]["lmList"][8]
                    hand2 = hands_data[1]["lmList"][8]

                    x1, y1 = hand1["x"], hand1["y"]
                    x2, y2 = hand2["x"], hand2["y"]

                    hand_center = np.array([(x1 + x2)/2, (y1 + y2)/2])

                    if zoom.pan_start is None:
                        zoom.pan_start = hand_center
                    else:
                        zoom.offset_x += (hand_center[0] - zoom.pan_start[0]) * zoom.scale
                        zoom.offset_y += (hand_center[1] - zoom.pan_start[1]) * zoom.scale
                        zoom.pan_start = hand_center

                    img = zoom.adjust(hands_data)

                else:
                    mode = "menu"
                    zoom.base_image = None
                    zoom.reset()
                    cooldown_frames = 15

        except Exception as e:
            print(f"Erreur: {str(e)}")
            mode = "menu"

        if cooldown_frames > 0:
            cooldown_frames -= 1

        cv2.imshow("Gesture Control", img)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
