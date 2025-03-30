import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
from configparser import ConfigParser

class HandController:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read('config.ini')
        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Screen dimensions
        self.screen_w, self.screen_h = pyautogui.size()
        
        # Camera settings
        self.camera_width = int(self.config['Settings']['camera_width'])
        self.camera_height = int(self.config['Settings']['camera_height'])
        
        # Window settings
        self.window_width = int(self.config['Settings']['window_width'])
        self.window_height = int(self.config['Settings']['window_height'])
        
        # Control parameters
        self.smoothing = float(self.config['Settings']['smoothing_factor'])
        self.click_thresh = float(self.config['Settings']['click_threshold'])
        self.scroll_sens = int(self.config['Settings']['scroll_sensitivity'])
        self.double_click_delay = float(self.config['Settings']['double_click_delay'])
        self.scroll_activation_thresh = float(self.config['Settings']['scroll_activation_thresh'])
        
        # State variables
        self.prev_x, self.prev_y = pyautogui.position()
        self.last_click_time = 0
        self.drag_mode = False

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.hands.process(rgb_frame)

    def get_gestures(self, results):
        gestures = {
            'left_click': False,
            'right_click': False,
            'double_click': False,
            'scroll': 0,
            'mouse_pos': None,
            'drag': False
        }

        if results.multi_hand_landmarks:
            try:
                hand = results.multi_hand_landmarks[0]
                landmarks = hand.landmark

                # Get key points
                index = self._get_landmark(landmarks, self.mp_hands.HandLandmark.INDEX_FINGER_TIP)
                thumb = self._get_landmark(landmarks, self.mp_hands.HandLandmark.THUMB_TIP)
                middle = self._get_landmark(landmarks, self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP)
                pinky = self._get_landmark(landmarks, self.mp_hands.HandLandmark.PINKY_TIP)
                wrist = self._get_landmark(landmarks, self.mp_hands.HandLandmark.WRIST)

                # Smooth cursor movement
                mouse_x = index['x'] * self.screen_w
                mouse_y = index['y'] * self.screen_h
                smoothed_x = self.prev_x + (mouse_x - self.prev_x) * self.smoothing
                smoothed_y = self.prev_y + (mouse_y - self.prev_y) * self.smoothing
                gestures['mouse_pos'] = (int(smoothed_x), int(smoothed_y))
                self.prev_x, self.prev_y = smoothed_x, smoothed_y

                # Click detection
                dist_index_thumb = self._distance(index, thumb)
                dist_middle_thumb = self._distance(middle, thumb)
                
                gestures['left_click'] = dist_index_thumb < self.click_thresh
                gestures['right_click'] = dist_middle_thumb < self.click_thresh
                
                # Double click detection
                if gestures['left_click']:
                    current_time = time.time()
                    if current_time - self.last_click_time < self.double_click_delay:
                        gestures['double_click'] = True
                    self.last_click_time = current_time

                # Scroll detection
                if self._distance(index, pinky) > self.scroll_activation_thresh:
                    scroll_value = (wrist['y'] - index['y']) * self.scroll_sens
                    gestures['scroll'] = int(scroll_value * 100)

                # Drag detection
                gestures['drag'] = dist_index_thumb < float(self.config['Settings']['drag_threshold'])

            except Exception as e:
                print(f"Gesture error: {e}")

        return gestures

    def _get_landmark(self, landmarks, landmark_id):
        return {'x': landmarks[landmark_id].x, 'y': landmarks[landmark_id].y}

    def _distance(self, p1, p2):
        return np.hypot(p1['x']-p2['x'], p1['y']-p2['y'])

    def draw_feedback(self, frame, gestures):
        try:
            h, w, _ = frame.shape
            
            # Convert screen coordinates to window coordinates
            if gestures['mouse_pos']:
                win_x = int(gestures['mouse_pos'][0] * self.window_width / self.screen_w)
                win_y = int(gestures['mouse_pos'][1] * self.window_height / self.screen_h)
                cv2.circle(frame, (win_x, win_y), 10, (0, 255, 0), 2)

            # Status text
            y_pos = 40
            status = [
                ("LEFT CLICK", gestures['left_click'], (0, 255, 0)),
                ("RIGHT CLICK", gestures['right_click'], (0, 0, 255)),
                ("DOUBLE CLICK", gestures['double_click'], (255, 255, 0)),
                (f"SCROLL: {gestures['scroll']}", gestures['scroll'] != 0, (255, 0, 255)),
                ("DRAG", gestures['drag'], (0, 255, 255))
            ]
            
            for text, condition, color in status:
                if condition:
                    cv2.putText(frame, text, (20, y_pos), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    y_pos += 35

        except Exception as e:
            print(f"Drawing error: {e}")
            
        return frame
