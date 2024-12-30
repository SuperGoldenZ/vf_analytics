"""Detecting Open Beta Splash Screen"""

import numpy as np
import cv2


class REVO:
    """Detects The Open Beta Splash Screen"""

    @staticmethod
    def is_beta_screen(image, debug):
        """Returns true if image is the Open Beta Splash Screen"""
        roi = image.copy()
        frame_height = roi.shape[0]
        gray_image = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # Apply a threshold to keep only the bright white colors
        threshold_value = 200

        _, thresholded_image = cv2.threshold(
            gray_image, threshold_value, 255, cv2.THRESH_BINARY
        )

        n_white_pix = 0

        n_white_pix = np.sum(thresholded_image == 255)

        if debug:
            cv2.imshow(f"threshold {n_white_pix}", thresholded_image)

            cv2.waitKey()
        if frame_height == 1080 and n_white_pix > 1000000:
            return True

        return False
