import pygetwindow as gw
import cv2
import numpy as np
import mss

class REVO:
    REVO_WINDOW_TITLE = "Virtua Fighter5 R.E.V.O."

    @staticmethod
    def get_window_bbox(window_title):
        """
        Get the bounding box (left, top, width, height) of the target window.
        """
        try:
            window = gw.getWindowsWithTitle(window_title)[0]
            if window.isMinimized:  # Ensure the window is not minimized
                window.restore()
            bbox = (window.left, window.top, window.right, window.bottom)
            return bbox
        except IndexError:
            print(f"Window with title '{window_title}' not found.")
            return None
        
    def capture_window(window_title=REVO_WINDOW_TITLE):
        """
        Capture video stream from a window with a specific title.
        """
        bbox = REVO.get_window_bbox(window_title)
        if bbox is None:
            return
        
        print(f"Capturing window: {window_title} at {bbox}")
        
        with mss.mss() as sct:
            monitor = {"top": bbox[1], "left": bbox[0], 
                    "width": bbox[2] - bbox[0], "height": bbox[3] - bbox[1]}
            
            while True:
                # Capture the screen region
                frame = np.array(sct.grab(monitor))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)  # Remove alpha channel
                
                # Show the frame in OpenCV window
                cv2.imshow("Captured Window", frame)
                
                # Exit condition: Press 'q' to exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break