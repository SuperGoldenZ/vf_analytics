"""This module provide functions to extract information from a VFES/US game frame"""

import cv2
import numpy as np


class CvHelper:
    """Helper classes for commonly used opencv functionality"""

    @staticmethod
    def count_pixels(target_color, image, override_tolerance=40):
        """Counts number of pixels around a certain color from an image"""
        tolerance = override_tolerance  # Adjust this value as needed

        # Convert the target color from hex to BGR
        target_color_bgr = tuple(int(target_color[i : i + 2], 16) for i in (5, 3, 1))

        # Define the lower and upper bounds for the color
        lower_bound = np.array(
            [max(c - tolerance, 0) for c in target_color_bgr], dtype=np.uint8
        )
        upper_bound = np.array(
            [min(c + tolerance, 255) for c in target_color_bgr], dtype=np.uint8
        )

        # Create a mask that identifies all pixels within the color range
        mask = cv2.inRange(image, lower_bound, upper_bound)

        # Count the number of non-zero (white) pixels in the mask
        return cv2.countNonZero(mask)
