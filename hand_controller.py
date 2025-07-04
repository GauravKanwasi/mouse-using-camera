import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
from configparser import ConfigParser
from threading import Lock

class HandController:
    _lock = Lock()
    
    def __init__(self):
        self.config = ConfigParser()
        self.config.read('config.ini')
        
        # Initialize MediaPipe with optimized settings
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.6,
            model_complexity=1  # Better accuracy for complex gestures [[3]]
        )
        
        # Screen dimensions
        self.screen_w, self.screen_h = pyautogui.size()
        
        # Load config values with environment overrides [[5]]
        self.camera_width = int(os.getenv("CAMERA_WIDTH", self.config['Settings']['camera_width']))
        self.camera_height = int(os.getenv("CAMERA_HEIGHT", self.config['Settings']['camera_height']))
        self.window_width = int(self.config['Settings']['window_width'])
        self.window_height = int(self.config['Settings']['window_height'])
        
        # Control parameters with adaptive thresholds [[1]]
        self.smoothing = float(os.getenv("MOUSE_SENSITIVITY", "0.6"))
        self.scroll_sens = int(os.getenv("SCROLL_SENSITIVITY", "20"))
        self.double_click_delay = float(self.config['Settings']['double_click_delay'])
        
        # State variables
        self.prev_x = self.prev_y = 0
        self.last_click_time = 0
        self.drag_mode = False
        self.scroll_buffer = []
        self.calibration_data = []

    def process_frame(self, frame):
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.results = self.hands.process(rgb_frame)
            return self.results
        except Exception as e:
            print(f"Frame processing error: {e}")
            return None

    def get_gestures(self):
        gestures = {
            'left_click': False,
            'right_click': False,
            'double_click': False,
            'scroll': 0,
            'mouse_pos': None,
            'drag': False,
            'results': self.results
        }

        if self.results and self.results.multi_hand_landmarks:
            try:
                hand = self.results.multi_hand_landmarks[0]
                landmarks = hand.landmark

                # Get key points
                index = self._get_landmark(landmarks, self.mp_hands.HandLandmark.INDEX_FINGER_TIP)
                thumb = self._get_landmark(landmarks, self.mp_hands.HandLandmark.THUMB_TIP)
                middle = self._get_landmark(landmarks, self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP)
                pinky = self._get_landmark(landmarks, self.mp_hands.HandLandmark.PINKY_TIP)
                wrist = self._get_landmark(landmarks, self.mp_hands.HandLandmark.WRIST)

                # Dynamic cursor smoothing [[1]]
                mouse_x = index['x'] * self.screen_w
                mouse_y = index['y'] * self.screen_h
                smoothed_x = self.prev_x + (mouse_x - self.prev_x) * self._adaptive_smoothing(index)
                smoothed_y = self.prev_y + (mouse_y - self.prev_y) * self._adaptive_smoothing(index)
                gestures['mouse_pos'] = (int(smoothed_x), int(smoothed_y))
                self.prev_x, self.prev_y = smoothed_x, smoothed_y

                # Click detection with adaptive thresholds [[1]]
                dist_index_thumb = self._distance(index, thumb)
                dist_middle_thumb = self._distance(middle, thumb)
                
                click_threshold = self._calibrate_threshold(dist_index_thumb)
                gestures['left_click'] = dist_index_thumb < click_threshold
                gestures['right_click'] = dist_middle_thumb < click_threshold
                
                # Double click detection [[8]]
                if gestures['left_click']:
                    current_time = time.time()
                    if current_time - self.last_click_time < self.double_click_delay:
                        gestures['double_click'] = True
                    self.last_click_time = current_time

                # Scroll detection with buffer [[6]]
                scroll_value = (wrist['y'] - index['y']) * self.scroll_sens
                self.scroll_buffer.append(scroll_value)
                if len(self.scroll_buffer) > 5:
                    self.scroll_buffer.pop(0)
                gestures['scroll'] = int(np.mean(self.scroll_buffer))

                # Drag detection [[9]]
                gestures['drag'] = dist_index_thumb < float(self.config['Settings']['drag_threshold'])

            except Exception as e:
                print(f"Gesture error: {e}")

        return gestures

    def _adaptive_smoothing(self, landmark):
        """Adjust smoothing factor based on hand movement dynamics [[1]]"""
        if hasattr(self, 'prev_landmark'):
            velocity = self._distance(landmark, self.prev_landmark)
            self.smoothing = max(0.3, min(0.8, 0.6 + velocity * 5))
        self.prev_landmark = landmark
        return self.smoothing

    def _calibrate_threshold(self, distance):
        """Adaptive threshold based on initial calibration data [[1]]"""
        if len(self.calibration_data) < 10:
            self.calibration_data.append(distance)
            return float(self.config['Settings']['click_threshold'])
        else:
            mean = np.mean(self.calibration_data)
            std = np.std(self.calibration_data)
            return mean - std  # 1σ below mean for better accuracy

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

            # Status text [[8]]
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
