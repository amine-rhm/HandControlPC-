import cv2
import mediapipe as mp
import math

import pyautogui
pyautogui.FAILSAFE = False


class HandDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None

    def find_hands(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        return img

    def get_landmarks(self, img):
        h, w = img.shape[:2]
        landmarks = []

        if self.results.multi_hand_landmarks:
            for hand in self.results.multi_hand_landmarks:
                hand_lms = []
                for id, lm in enumerate(hand.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    hand_lms.append({"id": id, "x": cx, "y": cy})
                landmarks.append({"lmList": hand_lms})
        return landmarks

    def fingers_up(self, hand_data, confidence=0.3):
        fingers = [0, 0, 0, 0, 0]
        if not hand_data["lmList"] or len(hand_data["lmList"]) < 21:
            return fingers

        # Pouce (basé sur la position X)
        if hand_data["lmList"][4]["x"] > hand_data["lmList"][3]["x"]:
            fingers[0] = 1

        # Autres doigts (basé sur la position Y)
        finger_tips = [8, 12, 16, 20]
        finger_pips = [6, 10, 14, 18]
        
        for i in range(4):
            tip_y = hand_data["lmList"][finger_tips[i]]["y"]
            pip_y = hand_data["lmList"][finger_pips[i]]["y"]
            if tip_y < pip_y - (30 * (1 + confidence)):
                fingers[i + 1] = 1

        return fingers
