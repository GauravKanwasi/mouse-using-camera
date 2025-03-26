import cv2
import pyautogui
from hand_controller import HandController

def main():
    controller = HandController()
    cap = cv2.VideoCapture(int(controller.config['Settings']['camera_id']))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(controller.config['Settings']['frame_width']))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(controller.config['Settings']['frame_height']))
    
    pyautogui.FAILSAFE = False
    drag_mode = False

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        results = controller.process_frame(frame)
        gestures = controller.get_gestures(results)

        if gestures['mouse_pos']:
            pyautogui.moveTo(*gestures['mouse_pos'])
            
            if gestures['left_click']:
                if not drag_mode:
                    pyautogui.mouseDown()
                    drag_mode = True
            else:
                if drag_mode:
                    pyautogui.mouseUp()
                    drag_mode = False

            if gestures['right_click']:
                pyautogui.rightClick()
                
            if gestures['scroll']:
                pyautogui.scroll(gestures['scroll'])

        frame = controller.draw_overlay(frame, gestures)
        cv2.imshow('Air Mouse Controller', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()