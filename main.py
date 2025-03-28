# main.py
import cv2
from gesture_detector import GestureDetector
from mouse_controller import MouseController
from config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT
import pyautogui

def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("Error: Could not access the camera.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    detector = GestureDetector()
    controller = MouseController()
    screen_width, screen_height = pyautogui.size()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        frame = cv2.flip(frame, 1)  # Mirror the frame
        gestures = detector.detect_gestures(frame)
        if gestures:
            index_tip = gestures['index_tip']
            controller.move_mouse(index_tip[0], index_tip[1], screen_width, screen_height)
            controller.click_if_gesture(gestures['landmarks'])

        cv2.imshow('Gesture Mouse Control', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
