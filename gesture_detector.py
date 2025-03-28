# gesture_detector.py
import cv2
import mediapipe as mp

class GestureDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        self.mp_drawing = mp.solutions.drawing_utils

    def detect_gestures(self, frame):
        """Detect hand gestures from the frame."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                # Example: Get index finger tip coordinates
                index_tip = hand_landmarks.landmark[8]
                return {
                    'index_tip': (int(index_tip.x * frame.shape[1]), int(index_tip.y * frame.shape[0])),
                    'landmarks': hand_landmarks.landmark
                }
        return None
