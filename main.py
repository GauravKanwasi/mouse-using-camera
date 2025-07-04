import cv2
import pyautogui
import os
import time
from threading import Thread
from hand_controller import HandController
from mediapipe.python.solutions.drawing_utils import draw_landmarks
from mediapipe.python.solutions.hands import HAND_CONNECTIONS

class MouseController:
    def __init__(self):
        self.controller = HandController()
        self.cap = None
        self.paused = False
        self.init_camera()
        
    def init_camera(self):
        self.cap = cv2.VideoCapture(int(self.controller.config['Settings']['camera_id']))
        if not self.cap.isOpened():
            raise RuntimeError("Camera access denied. Check permissions in System Settings.")
            
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.controller.camera_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.controller.camera_height)
        cv2.namedWindow('Air Mouse Controller', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Air Mouse Controller', 
                        self.controller.window_width, 
                        self.controller.window_height)
    
    def handle_gestures(self, gestures):
        if not self.paused and gestures['mouse_pos']:
            pyautogui.moveTo(*gestures['mouse_pos'])
            self.handle_clicks(gestures)
            self.handle_drag(gestures)
            self.handle_scroll(gestures)

    def handle_clicks(self, gestures):
        if gestures['double_click']:
            pyautogui.doubleClick()
        elif gestures['left_click']:
            pyautogui.click()
        if gestures['right_click']:
            pyautogui.rightClick()

    def handle_drag(self, gestures):
        if gestures['drag'] != self.controller.drag_mode:
            pyautogui.mouseDown() if gestures['drag'] else pyautogui.mouseUp()
            self.controller.drag_mode = gestures['drag']

    def handle_scroll(self, gestures):
        if gestures['scroll']:
            pyautogui.scroll(gestures['scroll'])

    def run(self):
        try:
            while True:
                success, frame = self.cap.read()
                if not success:
                    time.sleep(0.1)
                    continue
                
                frame = cv2.flip(frame, 1)
                
                # Parallel processing
                Thread(target=self.controller.process_frame, args=(frame,), daemon=True).start()
                gestures = self.controller.get_gestures()
                
                # Main thread for gesture handling
                Thread(target=self.handle_gestures, args=(gestures,), daemon=True).start()
                
                # Visual feedback
                frame_feedback = self.controller.draw_feedback(frame, gestures)
                if gestures['results'].multi_hand_landmarks:
                    for hand_landmarks in gestures['results'].multi_hand_landmarks:
                        draw_landmarks(frame_feedback, hand_landmarks, HAND_CONNECTIONS)
                        
                cv2.imshow('Air Mouse Controller', frame_feedback)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('p'):
                    self.paused = not self.paused
                    print(f"Gesture control {'paused' if self.paused else 'resumed'}")
                    
        except Exception as e:
            print(f"Critical error: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        print("Application closed gracefully.")

if __name__ == "__main__":
    controller = MouseController()
    controller.run()
