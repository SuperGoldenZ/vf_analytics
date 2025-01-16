"""This module provide functions to extract information from a VFES/US game frame"""

import cv2
import numpy as np
import vf_cv.cv_helper
import pytesseract

from line_profiler import profile


class Timer:
    """Interface for extracting time remaining in a round."""

    REGIONS_480P = {
        "time_seconds": (400, 15, 54, 34),
        "time_seconds_digit1": (403, 15, 25, 34),
        "time_seconds_digit2": (427, 15, 25, 34),
        "time_ms": (414, 48, 25, 14),
        "time_ms_digit1": (414, 48, 12, 14),
        "time_ms_digit2": (426, 48, 24, 14),
        "is_endround": (482, 0, 90, 14),
        "ko": (250, 170, 350, 140),
    }

    REGIONS_720P = {
        "is_endround": {725, 0, 135, 21},
        "p2_endround_other": (724, 65, 37, 5),
        "p1_endround_other": (164, 47, 394, 16),
        "time_seconds": (400, 15, 54, 34),
        "time_seconds_digit1": (403, 15, 25, 34),
        "time_seconds_digit2": (427, 15, 25, 34),
        "time_ms": (414, 48, 25, 14),
        "time_ms_digit1": (414, 48, 12, 14),
        "time_ms_digit2": (426, 48, 24, 14),
        "is_endround": (482, 0, 90, 14),
        "ko": (250, 170, 350, 140),
    }

    REGIONS_1080P = {
        "p2_endround_other": (1086, 98, 56, 8),
        "p1_endround_other": (246, 71, 591, 25),
        "time_seconds": (400, 15, 54, 34),
        "time_seconds_digit1": (403, 15, 25, 34),
        "time_seconds_digit2": (427, 15, 25, 34),
        "time_ms": (414, 48, 25, 14),
        "time_ms_digit1": (414, 48, 12, 14),
        "time_ms_digit2": (426, 48, 24, 14),
        "is_endround": (482, 0, 90, 14),
        "ko": (250, 170, 350, 140),
    }

    frame = None
    frame_height = None

    def __init__(self):
        self.rois = [None, None]
        self.n_white_pix = None
        self.quads = {}
        self.thresholded_image = None
        self.stage = None
        self.message = ""
        self.resized = False

        # self._model = load_model('best_model.keras')

    def set_frame(self, frame, stage=None):
        """Sets the image to extract data from"""
        self.frame = frame
        self.stage = stage
        self.frame_height = self.frame.shape[0]

    def get_roi(self, region_name):
        """Returns ROI based on resolution"""
        (x, y, w, h) = (0, 0, 0, 0)

        if self.frame_height == 360:
            (x, y, w, h) = self.REGIONS_480P[region_name]
            x = (int)(x * 0.75)
            y = (int)(y * 0.75)
            w = (int)(w * 0.75)
            h = (int)(h * 0.75)
        elif self.frame_height == 480:
            (x, y, w, h) = self.REGIONS_480P[region_name]
        elif self.frame_height == 720:
            (x, y, w, h) = self.REGIONS_720P[region_name]
            if not "other" in region_name:
                x = (int)(x * 1.5)
                y = (int)(y * 1.5)
                w = (int)(w * 1.5)
                h = (int)(h * 1.5)
        elif self.frame_height == 1080:
            (x, y, w, h) = self.REGIONS_1080P[region_name]
            if not "other" in region_name:
                x = (int)(x * 2.25)
                y = (int)(y * 2.25)
                w = (int)(w * 2.25)
                h = (int)(h * 2.25)
        return (x, y, w, h)

    def get_time_ms(self, debug=False):
        """Returns MS"""
        text = ""

        factor = 1.0

        for digit_num in range(1, 3):
            region_name = f"time_ms_digit{digit_num}"
            (x, y, w, h) = self.get_roi(region_name)

            x = int(x * factor)
            y = int(y * factor)
            w = int(w * factor)
            h = int(h * factor)

            roi = self.frame[y : y + h, x : x + w]
            gray_image = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            # Apply a threshold to keep only the bright white colors
            threshold_value = 125

            _, thresholded_image = cv2.threshold(
                gray_image, threshold_value, 255, cv2.THRESH_BINARY
            )

            contours, _ = cv2.findContours(
                thresholded_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            n_white_pix = 0

            if contours:
                x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
                thresholded_image = thresholded_image[y : y + h, x : x + w]

                height, width = (
                    thresholded_image.shape
                )  # Get the dimensions of the frame

            n_white_pix = np.sum(thresholded_image == 255)

            if debug is True:
                cv2.imshow(f"roi", roi)
                cv2.imshow(f"gray", gray_image)
                cv2.imshow(
                    f"thrsh h {self.frame_height}  width {width} {n_white_pix}",
                    thresholded_image,
                )
                cv2.waitKey()

            if self.frame_height == 1080:
                # Apply a threshold to keep only the bright white colors
                threshold_value = 203

                _, thresholded_image = cv2.threshold(
                    gray_image, threshold_value, 255, cv2.THRESH_BINARY
                )

                contours, _ = cv2.findContours(
                    thresholded_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )

                if contours:
                    x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
                    thresholded_image = thresholded_image[y : y + h, x : x + w]

                height, width = (
                    thresholded_image.shape
                )  # Get the dimensions of the frame

                digit, n_white_pix = Timer.get_time_ms_digit_1080(
                    thresholded_image, width, height
                )
                text = f"{text}{digit}"

            if self.frame_height == 720:
                height, width = thresholded_image.shape
                points = {}
                points[1] = thresholded_image[height - 1, 0]
                points[7] = thresholded_image[0, 0]
                points[9] = thresholded_image[0, width - 1]
                points[3] = thresholded_image[height - 1, width - 1]
                points[4] = thresholded_image[int(height / 2), 0]
                points[4.5] = thresholded_image[int(height / 2), int(width * 0.25)]
                points[5] = thresholded_image[int(height / 2), int(width / 2)]
                points[5.5] = thresholded_image[int(height / 2), int(width * 0.75)]
                points[59] = thresholded_image[int(height * 0.25), int(width * 0.75)]
                points[58] = thresholded_image[int(height * 0.25), int(width * 0.50)]
                points[57] = thresholded_image[int(height * 0.25), int(width * 0.25)]
                points[6] = thresholded_image[int(height / 2), width - 1]
                points[8] = thresholded_image[0, int(width / 2)]
                points[2.5] = thresholded_image[height - 1, int(width * 0.75)]
                points[2] = thresholded_image[height - 1, int(width / 2)]
                points[1.5] = thresholded_image[height - 1, int(width * 0.25)]

                if n_white_pix == 80:
                    text = f"{text}3"
                    continue

                if (
                    width == 12
                    and n_white_pix == 86
                    and points[8] != 0
                    and points[5] != 0
                    and points[2] != 0
                ):
                    text = f"{text}9"
                    continue

                if (
                    width == 11
                    and n_white_pix == 83
                    and points[8] != 0
                    and points[5] != 0
                    and points[2] != 0
                ):
                    text = f"{text}9"
                    continue

                if 86 <= n_white_pix <= 89 and points[8] != 0 and points[2] != 0:
                    text = f"{text}8"
                    continue

                if n_white_pix >= 90:
                    text = f"{text}8"
                    continue
                if n_white_pix >= 71 and points[5] == 0 and points[8] == 0:
                    text = f"{text}4"
                    continue

                if n_white_pix <= 36:
                    text = f"{text}1"
                    continue

                if (
                    points[5] != 0
                    and points[8] == 0
                    and points[2] != 0
                    and points[7] == 0
                    and points[1] == 0
                    and points[9] == 0
                    and points[3] == 0
                    and points[5.5] != 0
                    and points[4.5] != 0
                    and points[59] != 0
                ):  # and points[244] != 0
                    text = f"{text}8"
                elif (
                    points[5] != 0
                    and points[4] == 0
                    and points[4.5] != 0
                    and points[5.5] != 0
                    and points[57] != 0
                    and points[59] != 0
                ):
                    text = f"{text}9"
                elif points[8] != 0 and points[2] != 0 and points[2.5] != 0:
                    text = f"{text}6"
                elif (
                    points[9] != 0
                    and points[5] == 0
                    and points[2] != 0
                    and points[7] == 0
                    and points[1] == 0
                ) and points[59] == 0:
                    text = f"{text}5"
                elif points[9] != 0 and points[5] == 0:
                    text = f"{text}4"
                elif points[5] == 0 and points[8] != 0 and points[2] != 0:
                    text = f"{text}0"
                elif points[8] != 0 and points[2] != 0:
                    text = f"{text}3"
                elif (
                    points[5] == 0
                    and points[2] != 0
                    and points[9] == 0
                    and points[7] == 0
                    and points[1] != 0
                    and points[3] == 0
                ):
                    text = f"{text}2"
                elif points[5] != 0 and points[9] != 0 and points[1] != 0:
                    text = f"{text}7"
                elif points[9] != 0 and points[5] != 0:
                    text = f"{text}1"
                elif points[5] != 0:
                    if digit_num == 1:
                        text = f"{text}3"
                    else:
                        text = f"{text}9"

            elif self.frame_height == 480:
                n_white_pix = np.sum(thresholded_image == 255)
                height, width = (
                    thresholded_image.shape
                )  # Get the dimensions of the frame
                lower_left = thresholded_image[height - 1, 0]
                upper_right = thresholded_image[0, width - 1]
                lower_right = thresholded_image[height - 1, width - 1]
                upper_left = thresholded_image[0, 0]
                middle = thresholded_image[int(height / 2) - 1, int(width / 2)]

                if n_white_pix <= 22:
                    if (upper_right != 0 and upper_left == 0) or (
                        n_white_pix == 19 or n_white_pix == 20
                    ):
                        text = f"{text}7"
                    else:
                        text = f"{text}1"
                elif n_white_pix == 32 and upper_right != 0 and lower_left != 0:
                    text = f"{text}2"
                elif n_white_pix == 30:
                    text = f"{text}4"
                elif 32 <= n_white_pix <= 39 and middle != 0:
                    if (
                        upper_right != 0
                        and upper_left == 0
                        and lower_left == 0
                        and lower_right == 0
                        and n_white_pix != 32
                        and n_white_pix != 33
                    ):
                        text = f"{text}3"
                    else:
                        text = f"{text}6"
                elif n_white_pix == 36:
                    if middle == 0:
                        text = f"{text}0"
                    else:
                        text = f"{text}9"
                elif n_white_pix == 37 and middle == 0:
                    text = f"{text}0"
                elif n_white_pix == 38 or n_white_pix == 40:
                    text = f"{text}8"
                else:
                    text = f"{text}0"
        return text

    def is_time_running_out(self, debug_time=False):
        """Returns true if last 10 seconds of a round"""

        region_name = "time_seconds_digit1"
        (x, y, w, h) = self.get_roi(region_name)
        roi = self.frame[y : y + h, x : x + w]

        white = vf_cv.CvHelper.count_pixels("#FFFFFF", roi)
        count = vf_cv.CvHelper.count_pixels("#FF0000", roi)
        dr = vf_cv.CvHelper.count_pixels("#840003", roi)
        black = vf_cv.CvHelper.count_pixels("#000000", roi, override_tolerance=1)
        if debug_time is True:
            cv2.imshow(
                f"ro{self.frame_height} rc{count} dr{dr} w{white} bl{black}",
                roi,
            )
            cv2.waitKey()

        threshold = 100
        if h == 480:
            threshold = 50
        if self.frame_height == 360:
            threshold = 49

        if self.frame_height == 480 and dr > 275:
            return True

        if h == 720:
            threshold = 200
        if dr > 2000:
            return True

        if self.frame_height == 720:
            return count + dr > threshold and white < 300

        if self.frame_height == 360:
            if black > 16:
                return False

            return count + dr > threshold

        # if self.frame_height == 720:
        # return count +dr > threshold and white < 300

        return count > threshold

    @staticmethod
    def get_thresholded_image(gray_image, threshold_value):
        _, thresholded_image = cv2.threshold(
            gray_image, threshold_value, 255, cv2.THRESH_BINARY
        )

        contours = cv2.findContours(
            thresholded_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )[0]

        if contours:
            x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
            # Crop the image to the bounding box
            thresholded_image = thresholded_image[y : y + h, x : x + w]

        return thresholded_image

    def get_time_seconds_digit_480p(self, gray_image, digit_num, debug_time=False):
        thresholded_image = Timer.get_thresholded_image(gray_image, 200)

        height, width = thresholded_image.shape  # Get the dimensions of the frame

        factor = 1

        n_white_pix = np.sum(thresholded_image == 255)

        # endround is state when blue or red overlaps timer

        if debug_time is True:
            cv2.imshow("grey", gray_image)
            cv2.imshow(
                f"thrs {self.frame_height} {n_white_pix}  width {width} x {height}",
                thresholded_image,
            )
            cv2.waitKey()

        quads = {}
        quads[7], quads[9], quads[1], quads[3] = (
            vf_cv.CvHelper.count_white_pixels_in_four_sections(thresholded_image)
        )

        height, width = thresholded_image.shape  # Get the dimensions of the frame

        points = {}
        points[22] = thresholded_image[height - 2, int(width / 2)]
        points[2] = thresholded_image[height - 1, int(width / 2)]
        points[8] = thresholded_image[0, int(width / 2)]
        points[6] = thresholded_image[int(height / 2), width - 1]
        points[59] = thresholded_image[int(height / 2) - 2, int(width / 2)]
        points[58] = thresholded_image[int(height / 2) - 1, int(width / 2)]
        points[5] = thresholded_image[int(height / 2), int(width / 2)]
        points[4.5] = thresholded_image[int(height / 2),]
        points[1] = thresholded_image[height - 1, 0]
        points[1.5] = 0
        try:
            points[1.5] = thresholded_image[15, 0]
        except:
            points[1.5] = 0

        if (
            219 * factor <= n_white_pix <= 253 * factor
            or ((262 - 10) * factor <= n_white_pix <= 269 * factor)
            or (n_white_pix == 237)
        ) or (
            n_white_pix == 246
            or n_white_pix == 242
            or n_white_pix == 241
            or n_white_pix == 234
            or n_white_pix >= 266 * factor
            and n_white_pix <= 276 * factor
        ):
            color = thresholded_image[3, 3]

            veryupperleft = thresholded_image[0, 0]
            upperleft = thresholded_image[3, width - 1]
            upper_right = thresholded_image[0, width - 1]
            lower_right = thresholded_image[height - 1, width - 1]
            lowerleft = thresholded_image[height - 1, 0]
            lowerleft2 = thresholded_image[height - 2, 0]

            top_middle = thresholded_image[0, int(width * 0.5)]

            midleftquarter = thresholded_image[(int)(height / 2), int(width * 0.25)]
            middle = thresholded_image[int(height / 2), int(width / 2)]
            bottom_middle = thresholded_image[int(height * 0.75), int(width / 2)]
            midleft = thresholded_image[int(height / 2), 0]

            left_quarter = thresholded_image[int(height * 0.70), 0]
            thresholded_image[int(height * 0.70), 0] = 100

            # if (
            #  thresholded_image[6,16] == 0
            # and thresholded_image[4,14] == 0
            # )
            if (
                middle == 0
                and upper_right == 0
                and lowerleft == 0
                and veryupperleft == 0
                and lower_right == 0
                and midleftquarter != 0
                and top_middle != 0
                and thresholded_image[7, 17] != 0
                and thresholded_image[15, 3] != 0
                and thresholded_image[3, int(width / 2)] != 0
            ):
                return 0
            elif (
                points[5] == 0
                and points[2] != 0
                and points[8] != 0
                and thresholded_image[15, 3] != 0
                and thresholded_image[3, int(width / 2)] != 0
            ):
                return 0
            else:
                raise Exception("Undetectable digit 480p 01")

        elif n_white_pix == 252:
            raise Exception("unrecognizable digit 480p 02")

        elif n_white_pix >= 278 - 5:
            height, width = thresholded_image.shape  # Get the dimensions of the frame
            middle = thresholded_image[int(height / 2), int(width / 2)]
            middle2 = thresholded_image[int(height / 2) - 1, int(width / 2)]
            midleft = thresholded_image[int(height / 2), 0]
            upper_right = thresholded_image[int(height * 0.25), 0]

            if (
                middle == 0
                and middle2 == 0
                and upper_right == 0
                and thresholded_image[3, int(width / 2)] != 0
            ):
                return 0

            raise UnrecognizeTimeDigitException()
        raise UnrecognizeTimeDigitException()

    def get_time_seconds_digit_1080p(self, gray_image, digit_num, debug_time=False):
        thresholded_image = Timer.get_thresholded_image(gray_image, 200)

        height, width = thresholded_image.shape  # Get the dimensions of the frame

        n_white_pix_1080 = np.sum(thresholded_image == 255)
        n_white_top, n_white_bottom = vf_cv.cv_helper.CvHelper.count_pixels_top_bottom(
            thresholded_image
        )
        n_white_left, n_white_right = vf_cv.cv_helper.CvHelper.count_pixels_left_right(
            thresholded_image
        )

        quads = {}
        quads[7], quads[9], quads[1], quads[3] = (
            vf_cv.CvHelper.count_white_pixels_in_four_sections(thresholded_image)
        )

        if debug_time is True:
            cv2.imshow("grey", gray_image)
            cv2.imshow(
                f"th {self.frame_height} {n_white_pix_1080} :: {quads[7]} {quads[9]} {quads[1]} {quads[3]} width {width}",
                thresholded_image,
            )
            cv2.waitKey()

        upper_right = thresholded_image[0, width - 2]

        # 3 7 9 7

        # 4 3 7 9 5 2
        if n_white_top > n_white_bottom and n_white_right > n_white_left:
            if (
                thresholded_image[36, 8] == 0
                and width > 34
                and thresholded_image[14, 37] != 0
                and digit_num == 2
            ):
                return 9

        # 8 3 2 0
        if n_white_top < n_white_bottom and n_white_left < n_white_right:
            if (
                abs(n_white_top - n_white_bottom) < 5
                and abs(n_white_left - n_white_right) < 5
            ):
                return 0

        if abs(quads[9] - quads[1]) <= 15 and abs(quads[7] - quads[3]) <= 15:
            return 0

        if (
            n_white_top < n_white_bottom
            and n_white_left < n_white_right
            and digit_num == 2
        ):
            if n_white_pix_1080 < 1275 and thresholded_image[38, 20] == 0:
                return 3

            if (
                thresholded_image[15, 12] != 0
                and thresholded_image[9, 15] != 0
                and thresholded_image[38, 35] != 0
            ) and thresholded_image[int(height / 2), int(width / 2)] != 0:
                return 8

            if (
                thresholded_image[15, 12] != 0
                and thresholded_image[9, 15] != 0
                and thresholded_image[38, 35] != 0
            ) and thresholded_image[int(height / 2), int(width / 2)] != 0:
                return 8

        if 1545 - 10 <= n_white_pix_1080 <= 1545 + 10:
            return 8
        elif n_white_pix_1080 == 1264:
            return 2
        else:
            digit = self.get_time_digit(
                thresholded_image, width, height, digit_num, debug_time
            )
            return digit

    def get_digit_general(self, thresholded_image, debug):
        height, width = thresholded_image.shape

        points = {}

        points[7] = thresholded_image[0, 0]
        points[8] = thresholded_image[0, int(width / 2)]
        points[9] = thresholded_image[0, width - 1]

        points[4] = thresholded_image[int(height / 2), 0]
        points[5] = thresholded_image[int(height / 2), int(width / 2)]
        points[6] = thresholded_image[int(height / 2), width - 1]

        points[1] = thresholded_image[height - 1, 0]
        points[2] = thresholded_image[height - 1, int(width / 2)]
        points[3] = thresholded_image[height - 1, width - 1]

        if debug:
            cv2.imshow(f"gen {width} {height}")
            cv2.waitKey()

    def is_digit_one(self):
        height, width = self.thresholded_image.shape

        # Most white pixels in upper right quad
        if self.frame_height != 360 and self.quads[3] > self.quads[9]:
            return False

        if self.frame_height == 360:
            if 70 <= self.n_white_pix <= 80 and width < 15:
                return True

            if width >= 15:
                return False

            if (
                height > 6
                and width > 7
                # and self.thresholded_image[0, width - 1] != 0
                and self.thresholded_image[4, 0] == 0
                and self.thresholded_image[6, 7] == 0
            ):
                return False

            if (
                height > 4
                and self.thresholded_image[4, 1] == 0
                and self.thresholded_image[4, 0] == 0
            ):
                return False

            if self.n_white_pix >= 97 and not self.resized:
                return False

        if (
            self.frame_height != 480
            and self.frame_height != 360
            and self.quads[1] > self.quads[9]
        ):
            return False

        if self.quads[7] > self.quads[9]:
            return False

        if (
            self.frame_height != 480
            and self.frame_height != 360
            and self.thresholded_image[int(height / 2), int(width / 2)] == 0
        ):
            return False

        if self.frame_height == 720 and (width > 35 or self.n_white_pix > 430):
            return False

        if (self.frame_height == 480) and not (self.n_white_pix <= 175 and width < 18):
            return False

        if self.frame_height == 1080 and self.n_white_pix > 902 and width >= 35:
            return False

        if self.frame_height == 720 and self.n_white_pix > 400:
            return False

        return True

    def is_digit_two(self):
        height, width = self.thresholded_image.shape

        if self.frame_height == 360 and self.n_white_pix < 50:
            return False

        # Most white pixels in upper right quad
        if self.quads[3] > self.quads[9]:
            return False

        if self.quads[1] > self.quads[9]:
            if (
                not (
                    self.frame_height == 480
                    or self.frame_height == 720
                    or self.frame_height == 360
                )
                and abs(self.quads[9] - self.quads[1]) <= 5
            ):
                return False

        if self.quads[7] > self.quads[9]:
            return False

        # Second most in lower left quad
        if self.frame_height == 360:
            if width > 11 and height > 12 and self.thresholded_image[12, 11] != 0:
                return False

            if height > 9 and self.thresholded_image[9, 0] != 0:
                return False

        if self.frame_height != 360 and self.quads[3] > self.quads[1]:
            return False

        if self.quads[7] > self.quads[1]:
            return False

        # Bottom middle pixel should be colored
        if (
            self.thresholded_image[height - 1, int(width / 2)] == 0
            and self.thresholded_image[height - 2, int(width / 2)] == 0
        ):
            return False

        # Make sure middle is colored
        if (
            self.thresholded_image[int(height / 2), int(width / 2)] == 0
            and self.thresholded_image[int(height / 2) - 1, int(width / 2)] == 0
            and self.thresholded_image[int(height / 2) + 1, int(width / 2)] == 0
            and self.thresholded_image[int(height / 2) + 2, int(width / 2)] == 0
        ):
            return False

        # Upper left corner should be no color
        if self.thresholded_image[int(height * 0.35), int(width / 4)] != 0:
            return False

        if (
            self.frame_height == 360
            and height > 12
            and width > 12
            and self.thresholded_image[12, 12] != 0
        ):
            return False
        return True

    def is_digit_three(self):
        height, width = self.thresholded_image.shape

        # Most white pixels in upper right quad
        if (
            self.frame_height != 360
            and self.frame_height != 480
            and self.quads[3] > self.quads[9]
        ):
            # print("three - false 06")
            return False

        if (
            self.frame_height == 360
            and height > 8
            and width > 4
            and self.thresholded_image[8, 4] != 0
            and self.thresholded_image[8, 3] != 0
            and self.thresholded_image[8, 2] != 0
        ):
            # print("three - false 05")
            return False

        if (
            self.frame_height == 360
            and height > 9
            and self.thresholded_image[9, 2] != 0
        ):
            # print("false 9 0")
            return False

        # if self.thresholded_image[height-1, 0] != 0:
        # return False

        if (
            self.frame_height == 360
            and height > 5
            and self.thresholded_image[5, 5] != 0
            and self.thresholded_image[5 + 1, 5] != 0
        ):
            # print("three - false 04")
            return False

        if (
            self.frame_height == 360
            and height > 8
            and self.thresholded_image[8, 0] != 0
            and (height > 9 and self.thresholded_image[8 + 1, 0] != 0)
        ):
            # print("three - false 03")
            return False

        if self.quads[1] > self.quads[9]:
            if not (
                self.frame_height == 480 and abs(self.quads[9] - self.quads[1]) <= 3
            ):
                return False

        if self.quads[7] > self.quads[9]:
            return False

        # Second most in lower right quad
        if self.quads[1] > self.quads[3]:
            # print("false q1")
            return False

        if self.quads[7] > self.quads[3]:
            # print("false q2")
            return False

        # Upper left is smallest of all
        if (
            self.quads[7] > self.quads[1]
            and (self.frame_height != 360 or width > 12)
            and (self.n_white_pix < 110)
        ):
            # print("false q3")
            return False

        if (
            self.frame_height != 360
            and self.thresholded_image[int(height * 0.35), int(width / 4)] != 0
        ):
            # print("false q4")
            return False

        if self.frame_height != 360 and (
            self.thresholded_image[int(height * 0.5), int(width * 0.35) - 3] != 0
            or self.thresholded_image[int(height * 0.5), int(width * 0.35) - 1] != 0
            or self.thresholded_image[int(height * 0.5), int(width * 0.35) - 2] != 0
        ):
            # print("false q5")
            return False

        if self.frame_height == 720:
            if (
                self.thresholded_image[0, width - 1] != 0
                or self.thresholded_image[0, width - 2] != 0
                or self.thresholded_image[0, width - 1] != 0
                or self.thresholded_image[1, width - 2] != 0
            ):
                return False

        return True

    def is_digit_four(self):
        height, width = self.thresholded_image.shape

        # Most white pixels in upper right quad
        if self.quads[3] > self.quads[9] and self.frame_height != 360:
            return False

        if self.quads[1] > self.quads[9]:
            if not (
                self.frame_height == 480 and abs(self.quads[9] - self.quads[1]) <= 3
            ):
                return False

        if self.frame_height == 360:
            if self.quads[7] > self.quads[9]:
                return False

            # Second most in lower right quad
            if self.quads[1] > self.quads[3]:
                return False

            if self.quads[7] > self.quads[3]:
                return False

            # Upper left is smallest of all
            if self.quads[7] > self.quads[1]:
                return False

            if self.thresholded_image[height - 1, int(width * 0.25)] != 0:
                return False

            if self.thresholded_image[int(height * 0.25), int(width * 0.25)] != 0:
                return False

        if self.frame_height == 720:
            if self.n_white_pix < 525:
                return False
            if self.n_white_pix > 600:
                return False
            if (
                self.thresholded_image[0, width - 1] == 0
                and self.thresholded_image[0, width - 2] == 0
            ):
                return False
            if self.thresholded_image[0, 0] != 0:
                return False
            if self.thresholded_image[height - 1, width - 1] != 0:
                return False
            # print(f"{self.quads[3]} < {self.quads[1]}")
            if self.quads[7] > 100:
                return False

        # if (self.thresholded_image[int(height*0.5),int(width*0.35)] != 0):
        # return False

        return True

    def is_digit_five(self, digitnum, running_out):
        if digitnum == 1 and running_out is False:
            return False

        height, width = self.thresholded_image.shape

        # Most white pixels in upper right quad

        if self.frame_height != 480 and abs(self.quads[7] - self.quads[9]) > 30:
            return False

        # if self.thresholded_image[int(height*.65), int(width*0.25)] != 0:
        # return False

        # if self.thresholded_image[int(height*0.22), int(width*0.75)] != 0:
        # return False

        if self.frame_height == 360:
            if self.n_white_pix < 110:
                return False

            if height > 10 and self.thresholded_image[10, 2] != 0:
                return False

            if width > 13 and self.thresholded_image[5, 13] != 0:
                return False

            if (
                height > 9
                and self.thresholded_image[3, 9] != 0
                and self.thresholded_image[3, 10] != 0
            ):
                return False

            if self.thresholded_image[2, 0] != 0:
                return False

            if self.thresholded_image[6, 1] != 0 and self.thresholded_image[4, 1] != 0:
                return False

            if (
                self.thresholded_image[0, width - 1] == 0
                and self.thresholded_image[0, width - 2] == 0
                and self.thresholded_image[0, width - 3] == 0
            ):
                return False

        if self.frame_height == 480:
            # if self.quads[9] < self.quads[7] and self.quads[9] < self.quads[1] and self.quads[9] < self.quads[3]:
            # return False

            if self.thresholded_image[14, 3] != 0:
                return False

            if (
                self.thresholded_image.shape[1] > 16
                and self.thresholded_image[6, 16] != 0
            ):
                return False

            if (
                self.thresholded_image.shape[1] > 15
                and self.thresholded_image[7, 15] != 0
            ):
                return False

            if self.thresholded_image[5, 11] != 0:
                return False

            if (
                self.thresholded_image[15, 3] != 0
                or self.thresholded_image[14, 3] != 0
                or self.thresholded_image[15, 2] != 0
            ):
                return False

        if self.frame_height == 720:
            if (
                self.thresholded_image[0, width - 1] == 0
                and self.thresholded_image[0, width - 2] == 0
                and self.thresholded_image[0, width - 1] == 0
                and self.thresholded_image[1, width - 2] == 0
            ):
                return False

            if (
                self.thresholded_image[22, 4] != 0
                and self.thresholded_image[22, 3] != 0
                and self.thresholded_image[23, 4] != 0
                and self.thresholded_image[23, 3] != 0
            ):
                return False

        if self.frame_height == 1080:
            if self.quads[1] > self.quads[9]:
                return

        # if (self.quads[3] > self.quads[7] and abs(self.quads)):
        # return False

        # if (self.quads[3] > self.quads[9]):
        # return False

        # if self.frame_height != 1080:
        # if (self.quads[9] > self.quads[1]):
        # return False

        # if (self.quads[9] > self.quads[7]):
        # return False

        # if (self.quads[9] > self.quads[3]):
        # return False

        return True

    def is_digit_six(self, digit_num, running_out):
        height, width = self.thresholded_image.shape

        if digit_num == 1 and running_out is not True:
            return False

        if self.thresholded_image[0, 0] != 0:
            return False

        # if self.frame_height != 480:
        # if self.thresholded_image[0, width - 1] != 0:
        # return False

        if self.frame_height == 360:
            if width > 12 and self.thresholded_image[6, 12] != 0:
                # print("six - false 01")
                return False

        if self.frame_height == 480:
            if self.thresholded_image[10, 17] != 0:
                return False

        if (
            self.thresholded_image[int(height * 0.314), int(width * 0.9)] != 0
            and self.thresholded_image[int(height * 0.314), int(width * 0.9) - 1] != 0
            and self.thresholded_image[int(height * 0.314), int(width * 0.9) - 2] != 0
            and self.thresholded_image[int(height * 0.314), int(width * 0.9) - 3] != 0
        ):
            # print("six - false 02")
            return False

        if (
            self.thresholded_image[height - 1, int(width / 2)] == 0
            and self.thresholded_image[height - 2, int(width / 2)] == 0
            and self.thresholded_image[height - 3, int(width / 2)] == 0
            and self.thresholded_image[height - 4, int(width / 2)] == 0
            and self.thresholded_image[height - 2, int(width / 2) - 1] == 0
            and self.thresholded_image[height - 3, int(width / 2) - 1] == 0
            and self.thresholded_image[height - 4, int(width / 2) - 1] == 0
        ):
            # print("six - false 03")
            return False

        try:
            if (
                self.thresholded_image[height - 1, int(width / 2) + 4] == 0
                and self.thresholded_image[height - 2, int(width / 2) + 4] == 0
                and self.thresholded_image[height - 3, int(width / 2) + 4] == 0
                and self.thresholded_image[height - 4, int(width / 2) + 4] == 0
                and self.thresholded_image[height - 5, int(width / 2) + 4] == 0
                and self.thresholded_image[height - 6, int(width / 2) + 4] == 0
                and self.thresholded_image[height - 7, int(width / 2) + 4] == 0
            ):
                # print("six - false 04")
                return False
        except:
            # print("six - false 05")
            return False

        return True

    def is_digit_seven(self, digit_num, running_out):
        height, width = self.thresholded_image.shape

        if digit_num == 1 and running_out is not True:
            return False

        if self.frame_height == 360 and self.n_white_pix < 110:
            return True

        if self.frame_height == 360 and self.n_white_pix >= 120:
            return False

        if (
            self.thresholded_image[0, 0] == 0
            and self.thresholded_image[0, 1] == 0
            and self.thresholded_image[0, 2] == 0
            and self.thresholded_image[0, 3] == 0
            and self.thresholded_image[0, 4] == 0
            and self.thresholded_image[1, 0] == 0
            and self.thresholded_image[1, 1] == 0
            and self.thresholded_image[1, 2] == 0
            and self.thresholded_image[1, 3] == 0
            and self.thresholded_image[1, 4] == 0
        ):
            return False

        if self.frame_height == 480 and self.thresholded_image[8, 3] != 0:
            return False

        if self.frame_height == 360 and self.thresholded_image[3, 7] != 0:
            return False

        if self.frame_height == 360 and self.thresholded_image[13, 11] != 0:
            return False

        return True

    def is_digit_eight(self, digit_num, running_out):
        height, width = self.thresholded_image.shape

        if digit_num == 1 and running_out is not True:
            return False

        if self.frame_height == 360 and self.n_white_pix < 50:
            return False

        if (
            self.thresholded_image[0, 0] != 0
            and self.thresholded_image[0, 1] != 0
            and self.thresholded_image[0, 2] != 0
            and self.thresholded_image[0, 3] != 0
            and self.thresholded_image[0, 4] != 0
        ):
            return False

        if (
            self.frame_height == 360
            and height > 11
            and self.thresholded_image[11, 2] == 0
            and height > 12
            and self.thresholded_image[12, 2] == 0
        ):
            return False

        if self.frame_height == 360:
            if (
                self.thresholded_image[int(height / 2), int(width / 2)] == 0
                and self.thresholded_image[int(height / 2), int(width / 2) - 1] == 0
                and self.thresholded_image[int(height / 2) - 1, int(width / 2)] == 0
            ):
                return False
        else:
            if self.thresholded_image[int(height / 2), int(width / 2)] == 0:
                return False

        if (
            self.frame_height != 480
            and self.frame_height != 360
            and (self.quads[1] + self.quads[3] < self.quads[7] + self.quads[9])
        ):
            return False

        if self.frame_height == 480:
            if self.thresholded_image[15, 4] == 0:
                return False

        if (
            self.frame_height != 480
            and self.frame_height != 360
            and self.quads[3] < self.quads[7]
        ):
            return False

        if (
            self.frame_height != 480
            and self.frame_height != 360
            and self.quads[1] < self.quads[3]
        ):
            return False

        if self.frame_height == 720:
            if self.n_white_pix < 650:
                return False
            if self.quads[7] > self.quads[9]:
                return False
            if self.quads[9] < 165:
                return False

        return True

    def is_digit_nine(self, digit_num, running_out):
        height, width = self.thresholded_image.shape

        if digit_num == 1 and running_out is not True:
            return False

        # if self.quads[1] > self.quads[9] and not (
        # self.frame_height == 360 and running_out
        # ):
        # print("nine false 1")
        # return False

        if (
            self.thresholded_image[int(height / 2), int(width / 2)] == 0
            and self.thresholded_image[int(height / 2) + 1, int(width / 2)] == 0
            and self.thresholded_image[int(height / 2) + 2, int(width / 2)] == 0
            and self.thresholded_image[int(height / 2) + 1, int(width / 2) - 1] == 0
            and self.thresholded_image[int(height / 2) + 2, int(width / 2) - 1] == 0
            and self.thresholded_image[int(height / 2) + 1, int(width / 2) + 1] == 0
            and self.thresholded_image[int(height / 2) + 2, int(width / 2) + 1] == 0
            and self.thresholded_image[int(height / 2) + 1, int(width / 2) + 2] == 0
            and self.thresholded_image[int(height / 2) + 2, int(width / 2) + 2] == 0
            and self.thresholded_image[int(height / 2) + 1, int(width / 2) + 3] == 0
            and self.thresholded_image[int(height / 2) + 2, int(width / 2) + 3] == 0
        ):
            return False

        if (
            self.frame_height != 360
            and self.thresholded_image[int(height * 0.75), int(width * 0.2)] == 0
        ):
            return False

        if (
            self.frame_height == 360
            and height > 11
            and self.thresholded_image[11, 1] != 0
            and height >= 11
        ):
            # print("nine false 11")
            return False

        if (
            self.frame_height == 360
            and height > 12
            and self.thresholded_image[12, 2] != 0
            and height >= 12
        ):
            # print("nine false 11")
            return False

        if self.frame_height == 720:
            if self.n_white_pix < 610:
                return False
            if self.n_white_pix > 680:
                return False
            if self.quads[9] < 160:
                return False
            if self.quads[9] < self.quads[1]:
                return False
            # print(f"quads[1] {self.quads[1]}")
            if self.quads[1] > 165:
                return False

        return True

    def is_endround(self):
        height, width = self.thresholded_image.shape

        if self.frame_height == 360:
            if height <= 7 or width <= 7:
                return True

            if self.n_white_pix < 80 and self.thresholded_image[height - 1, 2] == 0:
                return True

        if self.frame_height == 720:
            if height <= 30:
                return True

        if self.frame_height == 480:
            if width <= 5 and height <= 15 or height <= 5:
                return True

            if width <= 13 and height <= 14:
                return True

            if self.n_white_pix == 0:
                return True

            if width <= 16 and height <= 18 and self.n_white_pix < 85:
                return True

            if width <= 18 and height <= 17:
                return True

            if width <= 18 and height <= 18 and self.n_white_pix < 155:
                return True

            if (
                width == 17
                and self.thresholded_image[height - 1, int(width / 2)] == 0
                and self.n_white_pix < 150
            ):
                return True

        return False

    def is_digit_zero(self, digit_num, running_out):
        if digit_num == 1 and running_out is False:
            return False

        height, width = self.thresholded_image.shape

        if self.thresholded_image[int(height / 2), int(width / 2)] != 0:
            return False

        if self.thresholded_image[int(height / 2), int(width * 0.25)] == 0:
            return False

        if self.frame_height == 720:
            if self.thresholded_image[14, 16] != 0:
                return False

        return True

    @profile
    def get_time_seconds(self, debug_time=False):
        """Returns number of seconds remaining in a round"""

        text = ""

        original_height = self.frame.shape[0]
        self.resized = False

        if original_height == 1080 or original_height == 720:
            self.frame = cv2.resize(self.frame, (640, 360))
            self.resized = True

        self.frame_height = self.frame.shape[0]

        factor = 1.0

        if self.frame_height == 360:
            factor = 0.75
        elif self.frame_height == 720:
            factor = 1.5
        elif self.frame_height == 1080:
            factor = 2.25

        for digit_num in range(1, 3):
            region_name = f"time_seconds_digit{digit_num}"
            old = self.frame_height
            self.frame_height = 480

            (x, y, w, h) = self.get_roi(region_name)

            self.frame_height = old

            x = int(x * factor)
            y = int(y * factor)
            w = int(w * factor)
            h = int(h * factor)

            running_out = self.is_time_running_out(debug_time)
            # print(f"time running out {running_out}")
            if running_out:
                x = (int)(x + (w / 2))
            roi = self.frame[y : y + h, x : x + w]

            blue_count = vf_cv.CvHelper.count_pixels("#5b1dc7", roi)

            # if self.frame_height != 360 and blue_count >= 5:
            #    return "endround"

            gray_image = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            self.rois[digit_num - 1] = roi

            if self.frame_height == 360:
                self.thresholded_image = Timer.get_thresholded_image(gray_image, 191)
            elif self.frame_height == 720:
                self.thresholded_image = Timer.get_thresholded_image(gray_image, 191)
            else:
                self.thresholded_image = Timer.get_thresholded_image(gray_image, 195)

            self.n_white_pix = np.sum(self.thresholded_image == 255)
            self.quads = {}
            self.quads[7], self.quads[9], self.quads[1], self.quads[3] = (
                vf_cv.CvHelper.count_white_pixels_in_four_sections(
                    self.thresholded_image
                )
            )
            if debug_time:
                cv2.imshow(
                    f"{self.frame_height} {self.thresholded_image.shape[1]} x {self.thresholded_image.shape[0]} :: {self.n_white_pix} :: {self.quads[7]} {self.quads[9]} {self.quads[1]} {self.quads[3]}",
                    self.thresholded_image,
                )
                cv2.imshow("original", roi)
                cv2.waitKey()

            if self.frame_height == 720:
                if debug_time:
                    print(f"\nget_time_seconds 720 {digit_num}")

                inverted = self.thresholded_image
                gray_image_t = 255 - inverted

                gray_image_t = vf_cv.CvHelper.add_white_column(gray_image_t, 15)
                gray_image_t = vf_cv.CvHelper.add_white_row(gray_image_t, 15)

                black_pix = np.sum(gray_image_t == 0)

                if black_pix <= 405:
                    # print(f"720 - setting digit_txt=1")
                    digit_text = "1"
                elif self.is_digit_seven(digit_num, running_out):
                    digit_text = "7"
                elif self.is_digit_four():
                    # print(f"720 - is digit four {self.is_digit_four()}")
                    digit_text = "4"
                elif self.is_digit_nine(digit_num, running_out):
                    # print(f"720 - is digit four {self.is_digit_four()}")
                    digit_text = "9"
                elif self.is_digit_eight(digit_num, running_out):
                    digit_text = "8"
                elif self.is_digit_five(digit_num, running_out):
                    digit_text = "5"
                elif self.is_digit_one():
                    digit_text = "1"
                elif self.is_digit_zero(digit_num, running_out):
                    digit_text = "0"
                elif self.is_digit_six(digit_num, running_out):
                    digit_text = "6"
                elif self.is_digit_three():
                    digit_text = "3"
                elif self.is_digit_two():
                    digit_text = "2"
                else:
                    raise UnrecognizeTimeDigitException(
                        "Unrecognized digit in 720p, skipping pytesseract for speed"
                    )
                    digit_text = pytesseract.image_to_string(
                        gray_image_t,
                        config="--psm 10 -c tessedit_char_whitelist=0123456789O",
                    ).strip()

                    digit_text = digit_text.replace("O", "0")
                    print(f"720 - doing PSR {digit_text}")
                    if digit_text == "":
                        if 670 <= black_pix <= 697:
                            digit_text = "8"

                    if debug_time:
                        cv2.imshow(
                            f"{self.thresholded_image.shape[1]} x {self.thresholded_image.shape[0]} :: {self.n_white_pix} :: {self.quads[7]} {self.quads[9]} {self.quads[1]} {self.quads[3]}",
                            gray_image_t,
                        )
                        cv2.imshow(
                            f"gray_image_t {black_pix}- [{digit_text}]", gray_image_t
                        )
                        cv2.waitKey()

                text = f"{text}{digit_text}"
                # print(f"720 [{digit_text}] -> {text}")
                if running_out:
                    return text
                continue
            else:
                if (
                    self.frame_height == 360
                    and self.thresholded_image.shape[1] == 13
                    and self.thresholded_image.shape[0] == 11
                    and self.n_white_pix == 72
                ):
                    text = f"{text}3"
                # elif self.is_endround():
                # return "endround"
                elif self.is_digit_one():
                    text = f"{text}1"
                elif self.is_digit_two():
                    text = f"{text}2"
                elif self.is_digit_three():
                    text = f"{text}3"
                elif self.is_digit_four():
                    text = f"{text}4"
                elif self.is_digit_five(digit_num, running_out):
                    text = f"{text}5"
                elif self.is_digit_six(digit_num, running_out):
                    text = f"{text}6"
                elif self.is_digit_seven(digit_num, running_out):
                    text = f"{text}7"
                elif self.is_digit_eight(digit_num, running_out):
                    text = f"{text}8"
                elif self.is_digit_nine(digit_num, running_out):
                    text = f"{text}9"
                elif self.is_digit_zero(digit_num, running_out):
                    text = f"{text}0"
                else:
                    raise UnrecognizeTimeDigitException("Unrecognized digit")
                    # return "endround"

            if running_out:
                return text

        if int(text) >= 70 and int(text) <= 79:
            return f"{int(text)-60}"

        if int(text) == 47:
            return "41"

        if float(text) < 0:
            raise InvalidTimeException(f"Found incorrect time {text}")

        if float(text) > 45:
            raise InvalidTimeException(f"Found incorrect time {text}")

        if debug_time:
            print(f"returning {text}")

        return text

    @staticmethod
    def get_time_ms_digit_1080(thresholded_image, width, height):
        n_white_pix = np.sum(thresholded_image == 255)

        points = {}
        if width <= 3 or height <= 3:
            return "0", n_white_pix

        points[4.8] = thresholded_image[int(height / 2) - 2, int(width / 2)]
        points[4.9] = thresholded_image[int(height / 2) - 1, int(width / 2)]
        points[5] = thresholded_image[int(height / 2), int(width / 2)]
        points[5.1] = thresholded_image[int(height / 2) + 1, int(width / 2)]
        points[6] = thresholded_image[int(height / 2) + 1, int(width / 2)]
        points[2] = thresholded_image[int(height) - 1, int(width / 2)]
        points[1.5] = 0

        upper_mid_right = 0
        lower_mid_left = 0

        try:
            points[33] = thresholded_image[12, width - 2]
            upper_mid_right = thresholded_image[14, 4]
            lower_mid_left = thresholded_image[12, 2]
            points[1.5] = thresholded_image[int(height * 0.70), 4]
        except:
            points[33] = 1
            upper_mid_right = 0
            lower_mid_left = 0

        if n_white_pix == 111 and width == 17:
            return "4", n_white_pix

        if (
            n_white_pix == 138
            and (
                points[4.9] != 0
                or points[5] != 0
                or points[5.1] != 0
                or points[4.8] != 0
            )
            and lower_mid_left == 0
        ):
            return "5", n_white_pix

        if (
            n_white_pix == 134
            and height == 18
            and width == 17
            and points[4.9] == 0
            and points[5] == 0
            and points[5.1] == 0
            and points[4.8] == 0
        ):
            return "0", n_white_pix

        if (
            n_white_pix == 138
            and height == 18
            and width == 17
            and points[4.9] == 0
            and points[5] == 0
            and points[5.1] == 0
            and points[4.8] == 0
        ):
            return "0", n_white_pix

        if (
            n_white_pix == 131
            or n_white_pix == 132
            or (n_white_pix == 127 and height == 17 and width == 17)
        ):
            return "9", n_white_pix

        if (
            n_white_pix == 138
            and height == 17
            and width == 17
            and (points[4.9] != 0 or points[5] != 0 or points[5.1] != 0)
        ):
            return "8", n_white_pix

        if height == 11:
            return "5", n_white_pix

        if (113 <= n_white_pix <= 122 or n_white_pix == 110) and width == 17:
            return "3", n_white_pix

        if (
            (
                n_white_pix == 104
                or n_white_pix == 121
                or n_white_pix == 122
                or n_white_pix == 124
                or n_white_pix == 105
            )
            and points[2] != 0
            and points[1.5] != 0
            and points[33] == 0
            and width == 18
        ):
            return "2", n_white_pix

        if (
            n_white_pix == 118
            and width == 15
            and (
                points[4.9] != 0
                or points[5] != 0
                or points[5.1] != 0
                or points[4.8] != 0
            )
            and lower_mid_left == 0
        ):
            return "5", n_white_pix

        if (
            n_white_pix == 123
            or n_white_pix == 124
            or (n_white_pix == 112 and width == 17)
            or (n_white_pix == 119 and width == 16)
            and (
                points[4.9] != 0
                or points[5] != 0
                or points[5.1] != 0
                or points[4.8] != 0
            )
            and lower_mid_left == 0
        ):
            return "5", n_white_pix

        if 143 <= n_white_pix <= 144 and width == 18:
            return "8", n_white_pix

        if 138 <= n_white_pix <= 138 and width == 17:
            return "6", n_white_pix

        if (
            n_white_pix == 133
            or n_white_pix == 148
            or 137 <= n_white_pix <= 140
            or n_white_pix == 149
            or n_white_pix == 152
            or n_white_pix == 153
            or n_white_pix == 154
            or n_white_pix == 141
            or n_white_pix == 150
        ) and points[4.9] != 0:
            return "8", n_white_pix

        if (
            n_white_pix == 130
            and width == 17
            and points[4.9] == 0
            and points[5] == 0
            and points[5.1] == 0
        ):
            return "0", n_white_pix

        if n_white_pix <= 74:
            return "1", n_white_pix

        if 79 <= n_white_pix <= 81:
            return "7", n_white_pix

        if n_white_pix == 144 and width == 17:
            return "6", n_white_pix

        if (
            130 <= n_white_pix <= 143
            or (n_white_pix == 128 and width == 17)
            or (126 <= n_white_pix <= 127 and width == 17)
            and upper_mid_right == 0
        ) and points[4.9] != 0:
            return "6", n_white_pix

        return "0", n_white_pix

    @staticmethod
    def get_time_digit(
        thresholded_image, width, height, digit_num, debug_time_digit=False
    ):
        """Returns one digit of the time remaining in a match"""

        n_white_pix = np.sum(thresholded_image == 255)

        quads = {}
        quads[7], quads[9], quads[1], quads[3] = (
            vf_cv.CvHelper.count_white_pixels_in_four_sections(thresholded_image)
        )

        n_white_top, n_white_bottom = vf_cv.cv_helper.CvHelper.count_pixels_top_bottom(
            thresholded_image
        )

        if debug_time_digit is True:
            cv2.imshow(
                f"g_t_s {height} {width} {n_white_pix} :: {quads[7]} {quads[9]} {quads[1]} {quads[3]} :: {n_white_top} {n_white_bottom}",
                thresholded_image,
            )
            cv2.waitKey()

        points = {}
        points[1] = thresholded_image[height - 1, 0]
        points[7] = thresholded_image[0, 0]
        points[9] = thresholded_image[0, width - 1]
        points[3] = thresholded_image[height - 1, width - 1]
        points[4] = thresholded_image[int(height / 2), 0]
        points[4.5] = thresholded_image[int(height / 2), int(width * 0.25)]
        points[5] = thresholded_image[int(height / 2), int(width / 2)]
        points[5.5] = thresholded_image[int(height / 2), int(width * 0.75)]
        points[59] = thresholded_image[int(height * 0.25), int(width * 0.75)]
        points[58] = thresholded_image[int(height * 0.25), int(width * 0.50)]
        points[57] = thresholded_image[int(height * 0.25), int(width * 0.25)]
        points[6] = thresholded_image[int(height / 2), width - 1]
        points[8] = thresholded_image[0, int(width / 2)]
        points[2] = thresholded_image[height - 1, int(width / 2)]
        points[1.5] = thresholded_image[height - 1, int(width * 0.25)]

        n_white_left, n_white_right = vf_cv.cv_helper.CvHelper.count_pixels_left_right(
            thresholded_image
        )

        try:
            points[244] = thresholded_image[24, 4]
            points["above_five"] = thresholded_image[
                int(height / 2) - 2, int(width / 2)
            ]
        except:
            return "00.00"

        if (
            thresholded_image[24, 24] != 0
            and thresholded_image[23, 6] != 0
            and thresholded_image[12, 26] != 0
        ):
            return 0

        if thresholded_image[16, 19] == 0 and thresholded_image[12, 26] != 0:
            return 0

        raise Exception(f"Invalid time digit {debug_time_digit}")

    def is_endround_other(self, debug_time=False):
        result = False

        for player_num in range(1, 3):
            (x, y, w, h) = self.get_roi(f"p{player_num}_endround_other")

            p2_life_roi = self.frame[y : y + h, x : x + w]
            dark_blue_left = vf_cv.CvHelper.count_pixels(
                "#020a80", p2_life_roi, override_tolerance=5
            )
            light_blue = vf_cv.CvHelper.count_pixels(
                "#4082f3", p2_life_roi, override_tolerance=50
            )
            arena_blue = vf_cv.CvHelper.count_pixels(
                "#0736a8", p2_life_roi, override_tolerance=50
            )
            lb2 = vf_cv.CvHelper.count_pixels(
                "#3a63e8", p2_life_roi, override_tolerance=50
            )
            maroon = vf_cv.CvHelper.count_pixels(
                "#530000", p2_life_roi, override_tolerance=5
            )

            yellow = vf_cv.CvHelper.count_pixels(
                "#f1f34c", p2_life_roi, override_tolerance=5
            )

            maroon_780 = vf_cv.CvHelper.count_pixels(
                "#5e1f00", p2_life_roi, override_tolerance=5
            )

            db = vf_cv.CvHelper.count_pixels(
                "#000d64", p2_life_roi, override_tolerance=15
            )

            if debug_time:
                cv2.imshow("full", self.frame)
                cv2.imshow(
                    f"{self.frame_height} p{player_num} y{yellow} m780[{maroon_780}] db{db} 1mr {maroon} lb2 {lb2} ab {arena_blue} lb {light_blue} dbl {dark_blue_left}",
                    p2_life_roi,
                )
                cv2.waitKey()

            if lb2 >= 3:
                self.message = f"p{player_num}_1"
                result = True

            if dark_blue_left >= 3:
                self.message = f"p{player_num}_2"
                result = True

            if light_blue >= 3:
                self.message = f"p{player_num}_3"
                result = True

            if arena_blue >= 3:
                self.message = f"p{player_num}_4"
                result = True

            if maroon >= 3:
                self.message = f"p{player_num}_5"
                result = True

            if db >= 100:
                self.message = f"p{player_num}_6"
                result = True

            if self.frame_height == 720:
                if yellow >= 10 and maroon_780 >= 10:
                    self.message = f"p{player_num}_7"
                    result = True

                if db >= 50:
                    self.message = f"p{player_num}_8"
                    result = True

        return result


class UnrecognizeTimeDigitException(Exception):
    pass


class InvalidTimeException(Exception):
    pass
