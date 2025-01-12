"""This module provide functions to extract information from a VFES/US game frame"""

import math
import cv2
import numpy as np
from skimage import color


class CvHelper:
    """Helper classes for commonly used opencv functionality"""

    target_bgr_lookup = {}
    lower_bound_lookup = {}
    upper_bound_lookup = {}

    @staticmethod
    def count_pixels(target_color, image, override_tolerance=40):
        """Counts number of pixels around a certain color from an image"""
        tolerance = override_tolerance  # Adjust this value as needed

        target_color_bgr = None
        lower_bound = None
        upper_bound = None
        lookup_key = f"{target_color}.{override_tolerance}"

        # Convert the target color from hex to BGR
        if lookup_key in CvHelper.target_bgr_lookup:
            target_color_bgr = CvHelper.target_bgr_lookup[lookup_key]
            lower_bound = CvHelper.lower_bound_lookup[lookup_key]
            upper_bound = CvHelper.upper_bound_lookup[lookup_key]
        else:
            target_color_bgr = tuple(
                int(target_color[i : i + 2], 16) for i in (5, 3, 1)
            )
            CvHelper.target_bgr_lookup[lookup_key] = target_color_bgr

            # Define the lower and upper bounds for the color
            lower_bound = np.array(
                [max(c - tolerance, 0) for c in target_color_bgr], dtype=np.uint8
            )
            upper_bound = np.array(
                [min(c + tolerance, 255) for c in target_color_bgr], dtype=np.uint8
            )

            CvHelper.upper_bound_lookup[lookup_key] = upper_bound
            CvHelper.lower_bound_lookup[lookup_key] = lower_bound

        # Create a mask that identifies all pixels within the color range
        mask = cv2.inRange(image, lower_bound, upper_bound)

        # Count the number of non-zero (white) pixels in the mask
        return cv2.countNonZero(mask)

    @staticmethod
    def count_pixels_top_bottom(image):
        height = image.shape[0]
        top_half = image[: height // 2]
        bottom_half = image[height // 2 :]

        # Count white pixels (255) in top and bottom halves
        count_top = cv2.countNonZero(top_half)
        count_bottom = cv2.countNonZero(bottom_half)

        return count_top, count_bottom

    @staticmethod
    def count_pixels_left_right(image):
        """Counts number of pixels around a certain color in the left and right halves of the image."""
        width = image.shape[1]
        left_half = image[:, : width // 2]
        right_half = image[:, width // 2 :]

        # Count white pixels (255) in left and right halves
        count_left = cv2.countNonZero(left_half)
        count_right = cv2.countNonZero(right_half)
        return count_left, count_right

    @staticmethod
    def count_white_pixels_in_four_sections(image):
        """Counts the number of white (255) pixels in the top-left, top-right, bottom-left, and bottom-right sections of the image."""
        height, width = image.shape

        # Split the image into four sections
        top_left = image[: height // 2, : width // 2]
        top_right = image[: height // 2, width // 2 :]
        bottom_left = image[height // 2 :, : width // 2]
        bottom_right = image[height // 2 :, width // 2 :]

        # Count white pixels (255) in each section
        count_top_left = cv2.countNonZero(top_left)
        count_top_right = cv2.countNonZero(top_right)
        count_bottom_left = cv2.countNonZero(bottom_left)
        count_bottom_right = cv2.countNonZero(bottom_right)

        return count_top_left, count_top_right, count_bottom_left, count_bottom_right

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

    @staticmethod
    def all_but_white(roi, lower=np.array([230, 230, 230])):
        lower_white = lower  # Lower bound of white color
        upper_white = np.array([255, 255, 255])  # Upper bound of white color
        mask = cv2.inRange(roi, lower_white, upper_white)

        # Apply the mask to keep only white areas in the ROI
        white_only_roi = cv2.bitwise_and(roi, roi, mask=mask)
        return white_only_roi

    @staticmethod
    def trim(roi):
        contours = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

        if contours:
            x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
            # Crop the image to the bounding box
            return roi[y : y + h, x : x + w]

        return roi

    @staticmethod
    def rgb_similarity(rgb1, rgb2):
        # Extract individual color components
        r1, g1, b1 = rgb1
        r2, g2, b2 = rgb2

        # Calculate Euclidean distance
        distance = math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)

        # Normalize distance to a scale of 0 to 1
        similarity = 1 - (distance / math.sqrt(3 * (255**2)))

        return similarity

    @staticmethod
    def rgb_to_lab(rgb):
        # Convert the RGB to LAB color space using OpenCV
        rgb_np = np.uint8([[list(rgb)]])  # Convert to a shape suitable for OpenCV
        lab = cv2.cvtColor(rgb_np, cv2.COLOR_RGB2LAB)
        return lab[0][0]

    @staticmethod
    def delta_e_ciede2000(lab1, lab2):
        # Convert LAB to a format suitable for delta E calculation
        lab1 = np.array(lab1).reshape(1, 1, 3)
        lab2 = np.array(lab2).reshape(1, 1, 3)

        # Use the skimage function to compute CIEDE2000
        delta_e = color.deltaE_ciede2000(lab1, lab2)
        return delta_e[0][0]

    @staticmethod
    def color_similarity(rgb1, rgb2):
        # Convert RGB to LAB
        lab1 = CvHelper.rgb_to_lab(rgb1)
        lab2 = CvHelper.rgb_to_lab(rgb2)

        # Calculate the color difference (lower means more similar)
        delta_e = CvHelper.delta_e_ciede2000(lab1, lab2)

        # Scale delta_e to a similarity score (smaller delta_e means more similar)
        similarity = max(0, 1 - (delta_e / 100))
        return similarity

    @staticmethod
    def get_thresholded_image(gray_image, threshold_value):

        _, thresholded_image = cv2.threshold(
            gray_image, threshold_value, 255, cv2.THRESH_BINARY
        )

        # contours = cv2.findContours(
        # thresholded_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        # )[0]

        # if contours:
        # x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
        # Crop the image to the bounding box
        # thresholded_image = thresholded_image[y : y + h, x : x + w]

        return thresholded_image

    @staticmethod
    def prepare_green_text_for_ocr(image):
        # Convert to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Define HSV range for light to dark green
        # green_lower = np.array([25, 100, 90])  # Lower bound for green
        green_lower = np.array([35, 100, 90])  # Lower bound for green
        green_upper = np.array([100, 255, 255])  # Upper bound for green

        # Create mask for green
        green_mask = cv2.inRange(hsv, green_lower, green_upper)

        # Invert the mask (green -> 0, everything else -> 255)
        inverted_mask = cv2.bitwise_not(green_mask)

        # Apply the inverted mask to create the final binary image
        binary_result = np.where(inverted_mask == 255, 255, 0).astype("uint8")

        return binary_result

    @staticmethod
    def blue_to_black(image):
        # Convert the image to HSV for easier color range selection
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Define the range for light blue in HSV
        # Adjust these values depending on the exact light blue color in your image
        lower_light_blue = np.array([50, 50, 50])  # Lower bound of light blue
        upper_light_blue = np.array([225, 255, 255])  # Upper bound of light blue

        # Create a mask for light blue pixels
        mask = cv2.inRange(hsv_image, lower_light_blue, upper_light_blue)

        # Replace light blue pixels with black in the original image
        image[mask > 0] = [0, 0, 0]
        return image

    @staticmethod
    def add_white_column(image, width, mono=False):
        height = image.shape[0]

        # Create a column of white pixels (255 for grayscale)
        # white_column = 255 * np.ones((height, 1), dtype=np.uint8)
        white_image = np.full((height, width), 255, dtype=np.uint8)

        # Concatenate the white column to the left of the image
        left_column = np.hstack((white_image, image))
        right_column = np.hstack((left_column, white_image))
        return right_column

    @staticmethod
    def add_white_row(image, height):
        # Get the width of the image
        width = image.shape[1]

        # Create a row of white pixels (255 for grayscale)
        # white_row = 255 * np.ones((1, width), dtype=np.uint8)
        white_row = np.full((height, width), 255, dtype=np.uint8)

        # Concatenate the white row to the bottom of the image
        bottom_row = np.vstack((image, white_row))
        return np.vstack((white_row, bottom_row))

    @staticmethod
    def deskew(image):
        coords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
        return rotated
