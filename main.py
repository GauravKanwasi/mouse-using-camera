import cv2
import pyautogui
from hand_controller import HandController

def main():
    controller = HandController()
    
    try:
        cap = cv2.VideoCapture(int(controller.config['Settings']['camera_id']))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, controller.frame_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, controller.frame_height)
    except Exception as e:
        print(f"Camera initialization failed: {e}")
        return

    pyautogui.FAILSAFE = False
    last_drag_state = False

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        results = controller.process_frame(frame)
        gestures = controller.get_gestures(results)
        
        if gestures['mouse_pos']:
            # Mouse movement
            pyautogui.moveTo(*gestures['mouse_pos'])
            
            # Click handling
            if gestures['double_click']:
                pyautogui.doubleClick()
            elif gestures['left_click']:
                pyautogui.click()
                
            if gestures['right_click']:
                pyautogui.rightClick()
                
            # Drag handling
            if gestures['drag'] and not last_drag_state:
                pyautogui.mouseDown()
                last_drag_state = True
            elif not gestures['drag'] and last_drag_state:
                pyautogui.mouseUp()
                last_drag_state = False
                
            # Scrolling
            if gestures['scroll']:
                pyautogui.scroll(gestures['scroll'])

        # Visual feedback
        frame = controller.draw_feedback(frame, gestures)
        cv2.imshow('Air Mouse Controller', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()