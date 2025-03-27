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
        
        self.screen_w, self.screen_h = pyautogui.size()
        self.prev_x, self.prev_y = pyautogui.position()
        self.last_click_time = 0
        self.drag_mode = False
        
        # Initialize parameters from config
        self.frame_width = int(self.config['Settings']['frame_width'])
        self.frame_height = int(self.config['Settings']['frame_height'])
        self.smoothing = float(self.config['Settings']['smoothing_factor'])
        self.click_thresh = float(self.config['Settings']['click_threshold'])
        self.scroll_sens = int(self.config['Settings']['scroll_sensitivity'])
        self.double_click_delay = float(self.config['Settings']['double_click_delay'])

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

                # Get key landmarks
                index = self._get_landmark_coords(landmarks, self.mp_hands.HandLandmark.INDEX_FINGER_TIP)
                thumb = self._get_landmark_coords(landmarks, self.mp_hands.HandLandmark.THUMB_TIP)
                middle = self._get_landmark_coords(landmarks, self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP)
                wrist = self._get_landmark_coords(landmarks, self.mp_hands.HandLandmark.WRIST)

                # Mouse position with smoothing
                mouse_x = index['x'] * self.screen_w
                mouse_y = index['y'] * self.screen_h
                smoothed_x = self.prev_x + (mouse_x - self.prev_x) * self.smoothing
                smoothed_y = self.prev_y + (mouse_y - self.prev_y) * self.smoothing
                gestures['mouse_pos'] = (int(smoothed_x), int(smoothed_y))
                self.prev_x, self.prev_y = smoothed_x, smoothed_y

                # Click detection
                dist_index_thumb = self._calculate_distance(index, thumb)
                dist_middle_thumb = self._calculate_distance(middle, thumb)
                
                gestures['left_click'] = dist_index_thumb < self.click_thresh
                gestures['right_click'] = dist_middle_thumb < self.click_thresh
                
                # Double click detection
                if gestures['left_click']:
                    current_time = time.time()
                    if current_time - self.last_click_time < self.double_click_delay:
                        gestures['double_click'] = True
                    self.last_click_time = current_time

                # Scroll detection
                scroll_base = self._calculate_distance(wrist, index)
                if scroll_base > 0.1:
                    scroll_value = (wrist['y'] - index['y']) * self.scroll_sens
                    gestures['scroll'] = int(scroll_value * 100)

                # Drag detection
                if dist_index_thumb < float(self.config['Settings']['drag_threshold']):
                    gestures['drag'] = True

            except Exception as e:
                print(f"Gesture error: {e}")

        return gestures

    def _get_landmark_coords(self, landmarks, landmark_id):
        return {
            'x': landmarks[landmark_id].x,
            'y': landmarks[landmark_id].y,
            'z': landmarks[landmark_id].z
        }

    def _calculate_distance(self, p1, p2):
        return np.sqrt((p1['x']-p2['x'])**2 + (p1['y']-p2['y'])**2)

    def draw_feedback(self, frame, gestures):
        try:
            h, w, _ = frame.shape
            
            # Draw cursor
            if gestures['mouse_pos']:
                screen_x, screen_y = gestures['mouse_pos']
                frame_x = int(screen_x * w / self.screen_w)
                frame_y = int(screen_y * h / self.screen_h)
                cv2.circle(frame, (frame_x, frame_y), 15, (0, 255, 0), 2)

            # Status text
            y_offset = 40
            colors = {
                'left_click': (0, 255, 0),
                'right_click': (0, 0, 255),
                'double_click': (255, 255, 0),
                'scroll': (255, 0, 255),
                'drag': (0, 255, 255)
            }
            
            for action, color in colors.items():
                if gestures.get(action, False):
                    text = action.replace('_', ' ').title()
                    if action == 'scroll' and gestures['scroll'] != 0:
                        text += f": {gestures['scroll']}"
                    cv2.putText(frame, text, (20, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                    y_offset += 40

        except Exception as e:
            print(f"Feedback error: {e}")
            
        return frame