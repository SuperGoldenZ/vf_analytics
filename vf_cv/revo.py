"""Detecting Open Beta Splash Screen"""

import numpy as np
import cv2
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
        ],
    }

    @staticmethod
    def is_beta_screen(image, debug):
        """Returns true if image is the Open Beta Splash Screen"""
        # roi = image.copy()

        frame_height = image.shape[0]
        for i in range(len(REVO.POINTS[frame_height])):
            point = REVO.POINTS[frame_height][i]

            (g, b, r) = image[point["y"], point["x"]]
            if g < 240 and r < 240 and b < 240:
                return False

        return True
