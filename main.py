import cv2
import pyautogui
from hand_controller import HandController

def main():
    controller = HandController()
    
    # Initialize camera
    cap = cv2.VideoCapture(int(controller.config['Settings']['camera_id']))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, controller.camera_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, controller.camera_height)
    
    # Create resizable window
    cv2.namedWindow('Air Mouse Controller', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Air Mouse Controller', 
                    controller.window_width, 
                    controller.window_height)
    
    pyautogui.FAILSAFE = False

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        results = controller.process_frame(frame)
        gestures = controller.get_gestures(results)
        
        if gestures['mouse_pos']:
            # Mouse control
            pyautogui.moveTo(*gestures['mouse_pos'])
            
            # Click handling
            if gestures['double_click']:
                pyautogui.doubleClick()
            elif gestures['left_click']:
                pyautogui.click()
                
            if gestures['right_click']:
                pyautogui.rightClick()
                
            # Drag handling
            if gestures['drag'] != controller.drag_mode:
                if gestures['drag']:
                    pyautogui.mouseDown()
                else:
                    pyautogui.mouseUp()
                controller.drag_mode = gestures['drag']
                
            # Scrolling
            if gestures['scroll']:
                pyautogui.scroll(gestures['scroll'])

        # Visual feedback
        frame = controller.draw_feedback(frame, gestures)
        
        # Display in resizable window
        cv2.imshow('Air Mouse Controller', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
