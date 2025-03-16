import cv2
import mediapipe as mp


class HandDetector:
    def __init__(self):
        # Initialisation du modèle MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
            model_complexity=1
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None
        self.handedness = []

    def find_hands(self, img):
        # Conversion BGR -> RGB et détection
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        self.handedness = []

        # Détection de la main gauche/droite
        if self.results.multi_handedness:
            for hand in self.results.multi_handedness:
                self.handedness.append(hand.classification[0].label)

        # Dessiner les landmarks
        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    img,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
        return img

    def get_landmarks(self, img):
        landmarks = []
        h, w, _ = img.shape

        if self.results.multi_hand_landmarks:
            for hand_num, hand in enumerate(self.results.multi_hand_landmarks):
                hand_data = {
                    "lmList": [],
                    "handedness": self.handedness[hand_num] if hand_num < len(self.handedness) else "Unknown"
                }

                for id, lm in enumerate(hand.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    hand_data["lmList"].append({"id": id, "x": cx, "y": cy})

                landmarks.append(hand_data)

        return landmarks

    def fingers_up(self, hand_data):
        fingers = []
        if not hand_data["lmList"]:
            return fingers

        # Pouce (dépend de la main gauche/droite)
        if hand_data["handedness"] == "Right":
            fingers.append(1 if hand_data["lmList"][4]["x"] > hand_data["lmList"][3]["x"] else 0)
        else:
            fingers.append(1 if hand_data["lmList"][4]["x"] < hand_data["lmList"][3]["x"] else 0)

        # Autres doigts
        for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:
            fingers.append(1 if hand_data["lmList"][tip]["y"] < hand_data["lmList"][pip]["y"] else 0)

        return fingers