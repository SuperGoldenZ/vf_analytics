"""This module provide functions to extract information from a VFES/US game frame"""

import cv2
import pytesseract
import vf_cv.cv_helper
from line_profiler import profile
import numpy as np


class Drinks:
    """Interface for extracting Shun's drink points from a round."""

    REGIONS_360P = {
        "p1": (43, 85, 26, 12),
        "p2": (604, 85, 26, 12),
    }

    REGIONS_720P = {
        "p1": (86, 170, 35, 20),
        "p2": (1206, 170, 35, 20),
    }

    frame = None
    frame_height = None

    def __init__(self, stage=None):
        self.rois = [None, None]
        self.n_white_pix = None
        self.quads = {}
        self.thresholded_image = None
        self.stage = stage

    def set_frame(self, frame):
        """Sets the image to extract data from"""
        self.frame = frame.copy()

        original_height = self.frame.shape[0]
        if original_height == 1080:
            self.frame = cv2.resize(self.frame, (1280, 720))

        self.frame_height = self.frame.shape[0]

    def get_roi(self, playernum):
        """Returns ROI based on resolution"""
        (x, y, w, h) = (0, 0, 0, 0)

        if self.frame_height == 360:
            (x, y, w, h) = self.REGIONS_360P[f"p{playernum}"]
            x = (int)(x * 1)
            y = (int)(y * 1)
            w = (int)(w * 1)
            h = (int)(h * 1)
        # elif self.frame_height == 480:
        # (x, y, w, h) = self.REGIONS_480P[region_name]
        elif self.frame_height == 720:
            (x, y, w, h) = self.REGIONS_720P[f"p{playernum}"]
            x = (int)(x * 1)
            y = (int)(y * 1)
            w = (int)(w * 1)
            h = (int)(h * 1)
        # elif self.frame_height == 1080:
        # (x, y, w, h) = self.REGIONS_480P[region_name]
        # x = (int)(x * 2.25)
        # y = (int)(y * 2.25)
        # w = (int)(w * 2.25)
        # h = (int)(h * 2.25)
        return (x, y, w, h)

    @profile
    def get_drink_points(self, playernum, debug=False):
        """Returns Shun Drink Points"""

        # Waterfalls stage is difficult because of white background
        if self.stage == "Waterfalls" and playernum == 1:
            return -1

        if self.stage == "Island":
            return -1

        if self.stage == "River" and playernum == 1:
            return -1

        text = ""

        (x, y, w, h) = self.get_roi(playernum)

        x = int(x)
        y = int(y)
        w = int(w)
        h = int(h)

        roi_original = self.frame[y : y + h, x : x + w]
        first_digit = self.frame[y : y + h, x : x + 10]
        second_digit = self.frame[y : y + h, x + 11 : x + 26]

        roi = vf_cv.CvHelper.blue_to_black(roi_original)

        # Define the condition: blue > 250 and red < 220 and green < 220
        condition = (roi[:, :, 0] > 220) & (roi[:, :, 1] < 220) & (roi[:, :, 2] < 220)

        # Replace these pixels with a new color, e.g., [0, 255, 0] (green)
        # roi[condition] = [0, 0, 0]

        # Define the condition: blue > 250 and red < 220 and green < 220
        condition = (roi[:, :, 0] > 190) & (roi[:, :, 1] < 214) & (roi[:, :, 2] < 220)
        # Replace these pixels with a new color, e.g., [0, 255, 0] (green)
        # roi[condition] = [0, 0, 0]

        # Define the condition: blue > 250 and red < 220 and green < 220
        if self.stage == "Waterfalls" and playernum == 1:
            condition = (
                (roi[:, :, 0] < 240) & (roi[:, :, 1] < 240) & (roi[:, :, 2] > 235)
            )
            # Replace these pixels with a new color, e.g., [0, 255, 0] (green)
            roi[condition] = [0, 0, 0]

            condition = (
                (roi[:, :, 0] < 215) & (roi[:, :, 1] > 220) & (roi[:, :, 2] > 220)
            )
            # Replace these pixels with a new color, e.g., [0, 255, 0] (green)
            roi[condition] = [0, 0, 0]

            condition = (
                (roi[:, :, 0] < 220) & (roi[:, :, 1] < 220) & (roi[:, :, 2] > 220)
            )
            # Replace these pixels with a new color, e.g., [0, 255, 0] (green)
            roi[condition] = [0, 0, 0]

            condition = (
                (roi[:, :, 0] < 245) & (roi[:, :, 1] < 245) & (roi[:, :, 2] > 245)
            )
            # Replace these pixels with a new color, e.g., [0, 255, 0] (green)
            roi[condition] = [0, 0, 0]

            condition = (
                (roi[:, :, 0] < 210) & (roi[:, :, 1] < 210) & (roi[:, :, 2] > 210)
            )
            # Replace these pixels with a new color, e.g., [0, 255, 0] (green)
            roi[condition] = [0, 0, 0]

            condition = (
                (roi[:, :, 0] < 215) & (roi[:, :, 1] < 215) & (roi[:, :, 2] > 215)
            )
            # Replace these pixels with a new color, e.g., [0, 255, 0] (green)
            roi[condition] = [0, 0, 0]

            condition = (
                (roi[:, :, 0] < 235) & (roi[:, :, 1] < 235) & (roi[:, :, 2] > 230)
            )
            # Replace these pixels with a new color, e.g., [0, 255, 0] (green)
            roi[condition] = [0, 0, 0]

            condition = (
                (roi[:, :, 0] < 245) & (roi[:, :, 1] < 245) & (roi[:, :, 2] > 245)
            )
            # Replace these pixels with a new color, e.g., [0, 255, 0] (green)
            roi[condition] = [0, 0, 0]

            condition = (
                (roi[:, :, 0] <= 230) & (roi[:, :, 1] <= 230) & (roi[:, :, 2] <= 230)
            )
            # Replace these pixels with a new color, e.g., [0, 255, 0] (green)
            roi[condition] = [0, 0, 0]

            condition = (
                (roi[:, :, 0] <= 248) & (roi[:, :, 1] <= 248) & (roi[:, :, 2] >= 245)
            )
            # Replace these pixels with a new color, e.g., [0, 255, 0] (green)
            roi[condition] = [0, 0, 0]

            condition = (
                (roi[:, :, 0] < 250) & (roi[:, :, 1] < 250) & (roi[:, :, 2] >= 254)
            )
            # Replace these pixels with a new color, e.g., [0, 255, 0] (green)
            roi[condition] = [0, 0, 0]

            condition = (
                (roi[:, :, 0] <= 250) & (roi[:, :, 1] <= 253) & (roi[:, :, 2] <= 251)
            )
            # Replace these pixels with a new color, e.g., [0, 255, 0] (green)
            roi[condition] = [0, 0, 0]

            condition = (
                (roi[:, :, 0] == 251) & (roi[:, :, 1] == 255) & (roi[:, :, 2] == 255)
            )
            # Replace these pixels with a new color, e.g., [0, 255, 0] (green)
            roi[condition] = [0, 0, 0]

        # Remove cloudy sky background on Island stage
        if self.stage == "Island":
            condition = (
                (roi[:, :, 0] > 235) & (roi[:, :, 1] < 235) & (roi[:, :, 2] < 235)
            )

            roi[condition] = [0, 0, 0]

            condition = (
                (roi[:, :, 0] > 250) & (roi[:, :, 1] < 241) & (roi[:, :, 2] < 241)
            )
            roi[condition] = [0, 0, 0]

            condition = (
                (roi[:, :, 0] > 190) & (roi[:, :, 1] < 180) & (roi[:, :, 2] < 180)
            )
            roi[condition] = [0, 0, 0]

            condition = (
                (roi[:, :, 0] > 210) & (roi[:, :, 1] < 195) & (roi[:, :, 2] < 195)
            )
            roi[condition] = [0, 0, 0]

            condition = (
                (roi[:, :, 0] > 225) & (roi[:, :, 1] < 220) & (roi[:, :, 2] < 220)
            )
            roi[condition] = [0, 0, 0]

            condition = (
                (roi[:, :, 0] > 215) & (roi[:, :, 1] < 210) & (roi[:, :, 2] < 210)
            )
            roi[condition] = [0, 0, 0]

            condition = (
                (roi[:, :, 0] > 205) & (roi[:, :, 1] < 205) & (roi[:, :, 2] < 205)
            )
            roi[condition] = [0, 0, 0]

        if self.frame_height == 360:
            roi = vf_cv.CvHelper.all_but_white(roi, lower=np.array([150, 150, 175]))
        elif self.frame_height == 720:
            roi = vf_cv.CvHelper.all_but_white(roi, lower=np.array([180, 180, 180]))

        gray_image = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        first_digit = cv2.cvtColor(first_digit, cv2.COLOR_BGR2GRAY)
        second_digit = cv2.cvtColor(second_digit, cv2.COLOR_BGR2GRAY)

        # Apply a threshold to keep only the bright white colors
        threshold_value = 125

        if self.frame_height == 720:
            threshold_value = 150

        _, thresholded_image = cv2.threshold(
            gray_image, threshold_value, 255, cv2.THRESH_BINARY
        )

        _, first_digit_threhold = cv2.threshold(
            first_digit, threshold_value, 255, cv2.THRESH_BINARY
        )

        _, second_digit_threhold = cv2.threshold(
            second_digit, threshold_value, 255, cv2.THRESH_BINARY
        )

        gray_image_t = 255 - thresholded_image
        first_digit_gray = 255 - first_digit_threhold
        second_digit_gray = 255 - second_digit_threhold

        first_digit_black_pix = np.sum(first_digit_gray == 0)
        second_digit_black_pix = np.sum(second_digit_gray == 0)

        gray_image_t = vf_cv.CvHelper.add_white_column(gray_image_t, 10)
        gray_image_t = vf_cv.CvHelper.add_white_row(gray_image_t, 10)

        first_digit_gray = vf_cv.CvHelper.add_white_column(first_digit_gray, 10)
        second_digit_gray = vf_cv.CvHelper.add_white_row(second_digit_gray, 10)

        second_digit_gray = vf_cv.CvHelper.add_white_column(second_digit_gray, 10)
        first_digit_gray = vf_cv.CvHelper.add_white_row(first_digit_gray, 10)

        black_pix = np.sum(gray_image_t == 0)

        text = pytesseract.image_to_string(
            gray_image_t, config="--psm 7 -c tessedit_char_whitelist=lLiI0123456789S"
        ).strip()

        if len(text) >= 3:
            text = text[:2]

        first_digit_text = pytesseract.image_to_string(
            first_digit_gray, config="--psm 7 -c tessedit_char_whitelist=123456789"
        ).strip()

        second_digit_text = pytesseract.image_to_string(
            second_digit_gray, config="--psm 7 -c tessedit_char_whitelist=123456789"
        ).strip()
        int_val = None

        try:
            int_val = int(text)
            if 70 <= int_val <= 79:
                int_val -= 70
        except:
            int_val = -1

        override_value = None

        if self.frame_height == 720:
            if self.stage == "Waterfalls" and playernum == 1:
                if 53 - 10 <= black_pix <= 53 + 10:
                    override_value = 7
            elif (
                135 <= black_pix <= 145
                and 29 <= first_digit_black_pix <= 35
                and 35 <= second_digit_black_pix <= 45
            ):
                override_value = 17
            elif (
                120 <= black_pix <= 133
                and 29 <= first_digit_black_pix <= 35
                and 29 <= second_digit_black_pix <= 35
            ):
                override_value = 11
            elif (
                black_pix > 48
                and black_pix < 70
                and second_digit_text != "2"
                and second_digit_text != "7"
                and second_digit_text != "4"
            ):
                override_value = 1
            elif 90 <= black_pix < 92 and second_digit_text != "4":
                override_value = 7
            elif text == "7" and black_pix <= 80 and first_digit_black_pix > 40:
                override_value = 1
            elif (
                second_digit_text == "7"
                and first_digit_black_pix < 40
                and black_pix > 100
                and second_digit_black_pix > 50
            ):
                override_value = 17
            elif (
                second_digit_text == "5"
                and first_digit_black_pix < 25
                and black_pix > 150
            ):
                override_value = 15
            elif (
                second_digit_text == "1"
                and first_digit_black_pix < 43
                and black_pix < 80
            ):
                override_value = 11
            elif (
                first_digit_text == "1"
                and second_digit_text == "1"
                and black_pix < 135
                and first_digit_black_pix <= 80
                and second_digit_black_pix <= 80
            ):
                override_value = 11
            elif (
                20 <= first_digit_black_pix <= 52
                and 20 <= second_digit_black_pix <= 52
                and second_digit_text != "7"
                and black_pix < 80
            ):
                override_value = 11
            elif first_digit_text == "7" and second_digit_text == "7":
                override_value = 17
            elif (
                first_digit_text == "1"
                and second_digit_text == "7"
                and second_digit_black_pix < 50
            ):
                override_value = 11
            elif first_digit_text == "7" and second_digit_text == "1":
                override_value = 11
            elif (
                first_digit_text == "1"
                and second_digit_text == "7"
                and 70 <= first_digit_black_pix <= 80
                and 81 <= second_digit_black_pix <= 90
            ):
                override_value = 17
            elif first_digit_text == "" and second_digit_text == "" and black_pix < 45:
                override_value = 1
            elif (
                first_digit_text == "4"
                and second_digit_text == "4"
                and first_digit_black_pix < 40
            ):
                override_value = 4
            elif (
                text == "42" and first_digit_text == "1" and first_digit_black_pix < 80
            ):
                override_value = 12
            elif int_val == -1 and first_digit_text == "1" and second_digit_text == "":
                override_value = 1
        if self.frame_height == 360 and 17 - 5 <= black_pix <= 17 + 5:
            override_value = 1

        gray_image_new = cv2.cvtColor(roi_original, cv2.COLOR_BGR2GRAY)
        gray_image_new = 255 - gray_image_new
        text = pytesseract.image_to_string(
            gray_image_new, config="--psm 7 -c tessedit_char_whitelist=0123456789"
        ).strip()

        if debug is True:
            cv2.imshow(f"frame", self.frame)
            cv2.imshow(f"roi", roi)
            cv2.imshow(
                f"first_digit {first_digit_black_pix} [{first_digit_text}]",
                first_digit_gray,
            )
            cv2.imshow(
                f"second_digit {second_digit_black_pix} [{second_digit_text}]",
                second_digit_gray,
            )
            cv2.imshow(f"roi_original", roi_original)
            cv2.imshow(f"gray", gray_image)
            cv2.imshow(f"gray_new {text}", gray_image_new)
            cv2.imshow(
                f"gray_t {black_pix} [{int_val}] override[{override_value}]",
                gray_image_t,
            )
            cv2.waitKey()

        if override_value is not None:
            return override_value

        if int_val < 0:
            return 0

        if int_val > 40:
            return 0

        return int_val
