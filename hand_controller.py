import cv2
import mediapipe as mp
import pyautogui
import numpy as np
from configparser import ConfigParser

class HandController:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.screen_w, self.screen_h = pyautogui.size()
        self.prev_x, self.prev_y = pyautogui.position()
        self.frame_shape = (int(self.config['Settings']['frame_height']),
                            int(self.config['Settings']['frame_width']), 3)

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        return results

    def get_gestures(self, results):
        gestures = {
            'left_click': False,
            'right_click': False,
            'scroll': 0,
            'mouse_pos': None,
            'drag': False
        }

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            landmarks = hand.landmark

            # Get key landmarks
            index_tip = landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = landmarks[self.mp_hands.HandLandmark.THUMB_TIP]
            middle_tip = landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            wrist = landmarks[self.mp_hands.HandLandmark.WRIST]

            # Mouse position with smoothing
            mouse_x = index_tip.x * self.screen_w
            mouse_y = index_tip.y * self.screen_h
            smoothed_x = self.prev_x + (mouse_x - self.prev_x) * float(self.config['Settings']['smoothing'])
            smoothed_y = self.prev_y + (mouse_y - self.prev_y) * float(self.config['Settings']['smoothing'])
            gestures['mouse_pos'] = (int(smoothed_x), int(smoothed_y))
            self.prev_x, self.prev_y = smoothed_x, smoothed_y

            # Click detection
            click_dist = np.hypot(index_tip.x - thumb_tip.x, index_tip.y - thumb_tip.y)
            right_click_dist = np.hypot(middle_tip.x - thumb_tip.x, middle_tip.y - thumb_tip.y)
            
            if click_dist < float(self.config['Settings']['click_threshold']):
                gestures['left_click'] = True
            if right_click_dist < float(self.config['Settings']['click_threshold']):
                gestures['right_click'] = True

            # Scroll detection
            scroll_base = np.hypot(wrist.x - index_tip.x, wrist.y - index_tip.y)
            if scroll_base > 0.1:
                scroll_value = (wrist.y - index_tip.y) * float(self.config['Settings']['scroll_sensitivity'])
                gestures['scroll'] = int(scroll_value * 100)

        return gestures

    def draw_overlay(self, frame, gestures):
        h, w, _ = frame.shape
        if gestures['mouse_pos']:
            # Draw cursor
            cx = int(gestures['mouse_pos'][0] * w / self.screen_w)
            cy = int(gestures['mouse_pos'][1] * h / self.screen_h)
            cv2.circle(frame, (cx, cy), 10, (0, 255, 0), 2)
            
            # Draw click status
            if gestures['left_click']:
                cv2.putText(frame, "LEFT CLICK", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            if gestures['right_click']:
                cv2.putText(frame, "RIGHT CLICK", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            if gestures['scroll']:
                cv2.putText(frame, f"SCROLL: {gestures['scroll']}", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        return frame