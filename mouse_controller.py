import pyautogui
from utils import calculate_distance, map_to_screen
from config import SMOOTHING_FACTOR, CLICK_THRESHOLD, FRAME_WIDTH, FRAME_HEIGHT

class MouseController:
    def __init__(self):
        self.prev_x, self.prev_y = pyautogui.position()

    def move_mouse(self, x, y, screen_width, screen_height):
        """Move the mouse cursor with smoothing."""
        screen_x, screen_y = map_to_screen(x, y, FRAME_WIDTH, FRAME_HEIGHT, screen_width, screen_height)
        smoothed_x = self.prev_x + SMOOTHING_FACTOR * (screen_x - self.prev_x)
        smoothed_y = self.prev_y + SMOOTHING_FACTOR * (screen_y - self.prev_y)
        pyautogui.moveTo(smoothed_x, smoothed_y)
        self.prev_x, self.prev_y = smoothed_x, smoothed_y

    def click_if_gesture(self, landmarks):
        """Simulate a click if the thumb and index finger are close enough."""
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        distance = calculate_distance((thumb_tip.x, thumb_tip.y), (index_tip.x, index_tip.y))
        if distance < CLICK_THRESHOLD:
            pyautogui.click()
