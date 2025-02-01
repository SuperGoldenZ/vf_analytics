"""Detecting Open Beta Splash Screen"""

import numpy as np
import cv2
import pytesseract
import vf_cv.cv_helper


class REVO:
    """Detects The Open Beta Splash Screen"""

    POINTS = {
        1080: [
            {"x": 489, "y": 71},
            {"x": 765, "y": 678},
            {"x": 1724, "y": 56},
            {"x": 1665, "y": 1068},
            {"x": 207, "y": 957},
        ],
        720: [
            {"x": 326, "y": 50},
            {"x": 494, "y": 372},
            {"x": 1124, "y": 617},
            {"x": 888, "y": 76},
            {"x": 578, "y": 414},
        ],
    }

    BLACK_POINTS = {
        720: [
            {"x": 0, "y": 0},
        ],
        1080: [
            {"x": 0, "y": 0},
        ],
    }

    @staticmethod
    def is_virtua_fighter_screen(image, debug):
        roi = image.copy()
        x, y, w, h = 372, 476, 1177, 126
        cropped = roi[y : y + h, x : x + w]

        # Convert to grayscale
        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

        # Invert the grayscale image
        inverted = cv2.bitwise_not(gray)

        # Convert #f5f5f5 to a grayscale value (approximately 245)
        threshold_value = int(0.85 * 255)  # Since #f5f5f5 is ~95% white

        # Set all pixels darker than #f5f5f5 to black
        _, processed = cv2.threshold(inverted, threshold_value, 255, cv2.THRESH_TOZERO)
        text = pytesseract.image_to_string(processed, timeout=2, config="--psm 7")

        if debug:
            print(text)
            cv2.imshow(f"vf {text}", processed)
            cv2.waitKey()

        if "tua" in text:
            return True

        if "Valrtua" in text:
            return True

        if "Fignter" in text:
            return True

        if "Virtua" in text:
            return True

        if "Fight" in text:
            return True

        return False

    @staticmethod
    def is_beta_screen(image, debug):
        """Returns true if image is the Open Beta Splash Screen"""
        roi = image.copy()

        frame_height = image.shape[0]
        for i in range(len(REVO.POINTS[frame_height])):
            point = REVO.POINTS[frame_height][i]

            (g, b, r) = image[point["y"], point["x"]]
            if g < 240 and r < 240 and b < 240:
                return False

        for i in range(len(REVO.BLACK_POINTS[frame_height])):
            point = REVO.BLACK_POINTS[frame_height][i]

            (g, b, r) = image[point["y"], point["x"]]
            if g > 100 and r > 100 and b > 100:
                return False

        return True
