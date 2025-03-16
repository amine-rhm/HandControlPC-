import pyautogui
import os
import time

class ScreenshotTaker:
    def __init__(self):
        self.folder = "screenshots"
        os.makedirs(self.folder, exist_ok=True)

    def capture(self):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.folder, f"capture_{timestamp}.png")
        pyautogui.screenshot(filename)