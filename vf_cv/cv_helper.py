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

    @staticmethod
    def compare_images_histogram(imageA, imageB):
        # Convert the images to HSV color space
        hsvA = cv2.cvtColor(imageA, cv2.COLOR_BGR2HSV)
        hsvB = cv2.cvtColor(imageB, cv2.COLOR_BGR2HSV)

        # Calculate the histograms
        histA = cv2.calcHist([hsvA], [0, 1], None, [50, 60], [0, 180, 0, 256])
        histB = cv2.calcHist([hsvB], [0, 1], None, [50, 60], [0, 180, 0, 256])

        # Normalize the histograms
        cv2.normalize(histA, histA, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        cv2.normalize(histB, histB, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

        # Compute the histogram intersection
        similarity = cv2.compareHist(histA, histB, cv2.HISTCMP_INTERSECT)
        return similarity
    
    @staticmethod
    def all_but_white_vftv(roi, lower=np.array([100, 100, 100])):
        lower_white = lower  # Lower bound of white color
        upper_white = np.array([255, 255, 255])  # Upper bound of white color
        mask = cv2.inRange(roi, lower_white, upper_white)

        # Apply the mask to keep only white areas in the ROI
        white_only_roi = cv2.bitwise_and(roi, roi, mask=mask)
        return white_only_roi
