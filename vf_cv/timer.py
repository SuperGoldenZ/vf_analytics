"""This module provide functions to extract information from a VFES/US game frame"""

import cv2
import numpy as np
import vf_cv.cv_helper


class Timer:
    """Interface for extracting time remaining in a round."""

    REGIONS_480P = {
        "time_seconds": (400, 15, 54, 34),
        "time_seconds_digit1": (403, 15, 25, 34),
        "time_seconds_digit2": (427, 15, 25, 34),
        "time_ms": (414, 48, 25, 14),
        "time_ms_digit1": (414, 48, 12, 14),
        "time_ms_digit2": (426, 48, 24, 14),
        "is_endround": {482, 0, 90, 14},
    }

    REGIONS_720P = {"is_endround": {725, 0, 135, 21}}

    frame = None
    frame_height = None

    def __init__(self):
        self.rois = [None, None]
        self.n_white_pix = None
        self.quads = {}
        self.thresholded_image = None

        # self._model = load_model('best_model.keras')

    def set_frame(self, frame):
        """Sets the image to extract data from"""
        self.frame = frame
        self.frame_height = frame.shape[0]

    def get_roi(self, region_name):
        """Returns ROI based on resolution"""
        (x, y, w, h) = (0, 0, 0, 0)

        if self.frame_height == 480:
            (x, y, w, h) = self.REGIONS_480P[region_name]
        elif self.frame_height == 720:
            (x, y, w, h) = self.REGIONS_480P[region_name]
            x = (int)(x * 1.5)
            y = (int)(y * 1.5)
            w = (int)(w * 1.5)
            h = (int)(h * 1.5)
        elif self.frame_height == 1080:
            (x, y, w, h) = self.REGIONS_480P[region_name]
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

        if debug_time is True:
            cv2.imshow(
                f"running_out {self.frame_height} redcount {count}   dr {dr}  {white}",
                roi,
            )
            cv2.waitKey()

        threshold = 100
        if h == 480:
            threshold = 50

        if self.frame_height == 480 and dr > 275:
            return True

        if h == 720:
            threshold = 200
        if dr > 2000:
            return True

        if self.frame_height == 720:
            return count + dr > threshold and white < 300

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

            raise Exception("Unrecognized time")
        raise Exception("Unrecognized time")

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
        if self.quads[3] > self.quads[9]:
            return False

        if self.frame_height != 480 and self.quads[1] > self.quads[9]:
            return False

        if self.quads[7] > self.quads[9]:
            return False

        if (
            self.frame_height != 480
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

        # Most white pixels in upper right quad
        if self.quads[3] > self.quads[9]:
            return False

        if self.quads[1] > self.quads[9]:
            if (
                not (self.frame_height == 480 or self.frame_height == 720)
                and abs(self.quads[9] - self.quads[1]) <= 5
            ):
                return False

        if self.quads[7] > self.quads[9]:
            return False

        # Second most in lower left quad
        if self.quads[3] > self.quads[1]:
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

        return True

    def is_digit_three(self):
        height, width = self.thresholded_image.shape

        # Most white pixels in upper right quad
        if self.frame_height != 480 and self.quads[3] > self.quads[9]:
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
            return False

        if self.quads[7] > self.quads[3]:
            return False

        # Upper left is smallest of all
        if self.quads[7] > self.quads[1]:
            return False

        if self.thresholded_image[int(height * 0.35), int(width / 4)] != 0:
            return False

        if (
            self.thresholded_image[int(height * 0.5), int(width * 0.35) - 3] != 0
            or self.thresholded_image[int(height * 0.5), int(width * 0.35) - 1] != 0
            or self.thresholded_image[int(height * 0.5), int(width * 0.35) - 2] != 0
        ):
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
        if self.quads[3] > self.quads[9]:
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

        # if self.frame_height == 1080:
        # if self.quads[3] + self.quads[1] < self.quads[7] + self.quads[9]:
        # print("quads six false")
        # return False

        if self.frame_height != 480:
            if self.thresholded_image[0, width - 1] != 0:
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
            return False

        if (
            self.thresholded_image[height - 1, int(width / 2)] == 0
            and self.thresholded_image[height - 2, int(width / 2)] == 0
            and self.thresholded_image[height - 3, int(width / 2)] == 0
            and self.thresholded_image[height - 4, int(width / 2)] == 0
        ):
            return False

        if (
            self.thresholded_image[height - 1, int(width / 2) + 4] == 0
            and self.thresholded_image[height - 2, int(width / 2) + 4] == 0
            and self.thresholded_image[height - 3, int(width / 2) + 4] == 0
            and self.thresholded_image[height - 4, int(width / 2) + 4] == 0
            and self.thresholded_image[height - 5, int(width / 2) + 4] == 0
        ):
            return False

        return True

    def is_digit_seven(self, digit_num, running_out):
        height, width = self.thresholded_image.shape

        if digit_num == 1 and running_out is not True:
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

        return True

    def is_digit_eight(self, digit_num, running_out):
        height, width = self.thresholded_image.shape

        if digit_num == 1 and running_out is not True:
            return False

        if (
            self.thresholded_image[0, 0] != 0
            and self.thresholded_image[0, 1] != 0
            and self.thresholded_image[0, 2] != 0
            and self.thresholded_image[0, 3] != 0
            and self.thresholded_image[0, 4] != 0
        ):
            return False

        if self.thresholded_image[int(height / 2), int(width / 2)] == 0:
            return False

        if self.frame_height != 480 and (
            self.quads[1] + self.quads[3] < self.quads[7] + self.quads[9]
        ):
            return False

        if self.frame_height == 480:
            if self.thresholded_image[15, 4] == 0:
                return False

        if self.frame_height != 480 and self.quads[3] < self.quads[7]:
            return False

        if self.frame_height != 480 and self.quads[1] < self.quads[3]:
            return False

        return True

    def is_digit_nine(self, digit_num, running_out):
        height, width = self.thresholded_image.shape

        if digit_num == 1 and running_out is not True:
            return False

        if self.quads[1] > self.quads[9]:
            return False

        if (
            self.thresholded_image[int(height / 2), int(width / 2)] == 0
            and self.thresholded_image[int(height / 2) + 1, int(width / 2)] == 0
            and self.thresholded_image[int(height / 2) + 2, int(width / 2)] == 0
        ):
            return False

        if self.thresholded_image[int(height * 0.75), int(width * 0.2)] == 0:
            return False

        return True

    def is_endround(self):
        height, width = self.thresholded_image.shape

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

        return True

    def get_time_seconds(self, debug_time=False):
        """Returns number of seconds remaining in a round"""

        text = ""

        factor = 1.0

        if self.frame_height == 720:
            factor = 1.5
        elif self.frame_height == 1080:
            factor = 2.25

        if self.frame_height == 480:
            is_endround_roi = self.frame[0:14, 402 : 402 + 90]

            dark_blue_left = vf_cv.CvHelper.count_pixels(
                "#1a2cd1", is_endround_roi, override_tolerance=10
            )
            dark_blue_right = vf_cv.CvHelper.count_pixels("#0e3e97", is_endround_roi)
            dark_blue_right_two = vf_cv.CvHelper.count_pixels(
                "#3f4d74", is_endround_roi, override_tolerance=5
            )

            light_blue = vf_cv.CvHelper.count_pixels(
                "#999fe4", is_endround_roi, override_tolerance=10
            )
            light_blue_two = vf_cv.CvHelper.count_pixels(
                "#aaa0e8", is_endround_roi, override_tolerance=10
            )
            light_blue_three = vf_cv.CvHelper.count_pixels(
                "#92aaff", is_endround_roi, override_tolerance=10
            )

            if debug_time:
                cv2.imshow(
                    f"{dark_blue_left} {dark_blue_right} {dark_blue_right_two} {light_blue} {light_blue_two} {light_blue_three}",
                    is_endround_roi,
                )
                cv2.waitKey()

            if dark_blue_right >= 10 and light_blue >= 5:
                return "endround"

        if self.frame_height == 1080:
            is_endround_roi = self.frame[0:38, 1088 : 1088 + 203]

            dark_blue_left = vf_cv.CvHelper.count_pixels(
                "#1a2cd1", is_endround_roi, override_tolerance=10
            )
            dark_blue_right = vf_cv.CvHelper.count_pixels("#0e3e97", is_endround_roi)
            dark_blue_right_two = vf_cv.CvHelper.count_pixels(
                "#3f4d74", is_endround_roi, override_tolerance=5
            )

            light_blue = vf_cv.CvHelper.count_pixels(
                "#999fe4", is_endround_roi, override_tolerance=10
            )
            light_blue_two = vf_cv.CvHelper.count_pixels(
                "#aaa0e8", is_endround_roi, override_tolerance=10
            )
            light_blue_three = vf_cv.CvHelper.count_pixels(
                "#92aaff", is_endround_roi, override_tolerance=10
            )

            if debug_time:
                cv2.imshow(
                    f"{dark_blue_left} {dark_blue_right} {dark_blue_right_two} {light_blue} {light_blue_two} {light_blue_three}",
                    is_endround_roi,
                )
                cv2.waitKey()

            if (dark_blue_right > 110 or dark_blue_right_two > 40) and (
                light_blue >= 1 or light_blue_two >= 1 or light_blue_three >= 1
            ):
                return "endround"

        if self.frame_height == 720:
            is_endround_roi = self.frame[0:25, 725 : 725 + 135]

            dark_blue_left = vf_cv.CvHelper.count_pixels(
                "#1a2cd1", is_endround_roi, override_tolerance=10
            )
            dark_blue_right = vf_cv.CvHelper.count_pixels(
                "#0e3e97", is_endround_roi, 30
            )
            dark_blue_right_two = vf_cv.CvHelper.count_pixels(
                "#3f4d74", is_endround_roi, override_tolerance=5
            )

            light_blue = vf_cv.CvHelper.count_pixels(
                "#999fe4", is_endround_roi, override_tolerance=10
            )
            light_blue_two = vf_cv.CvHelper.count_pixels(
                "#aaa0e8", is_endround_roi, override_tolerance=10
            )
            light_blue_three = vf_cv.CvHelper.count_pixels(
                "#92aaff", is_endround_roi, override_tolerance=10
            )
            dark_blue_right_three = vf_cv.CvHelper.count_pixels(
                "#44447b", is_endround_roi, override_tolerance=5
            )

            white = vf_cv.CvHelper.count_pixels(
                "#dbe9f3", is_endround_roi, override_tolerance=5
            )

            pb = vf_cv.CvHelper.count_pixels(
                "#3032bb", is_endround_roi, override_tolerance=15
            )

            purp = vf_cv.CvHelper.count_pixels(
                "#6f137b", is_endround_roi, override_tolerance=5
            )
            purp2 = vf_cv.CvHelper.count_pixels(
                "#682a64", is_endround_roi, override_tolerance=5
            )

            roi_bw = cv2.cvtColor(is_endround_roi, cv2.COLOR_BGR2GRAY)

            if debug_time:
                cv2.imshow("bw", roi_bw)
                cv2.imshow(
                    f"purp {purp} pb {pb} wh {white} {dark_blue_left} dbr: {dark_blue_right} dbr2: {dark_blue_right_two} lb: {light_blue} lb2: {light_blue_two} {light_blue_three} thr: {dark_blue_right_three}",
                    is_endround_roi,
                )

                cv2.imshow("frame", self.frame)
                cv2.waitKey()

            if (
                pb > 0
                or light_blue > 100
                or (light_blue > 30 and light_blue_two > 30)
                or dark_blue_right > 900
            ) and (purp == 0 and purp2 == 0):
                if dark_blue_right >= 3 and light_blue >= 5 and light_blue_three >= 1:
                    return "endround"

                if dark_blue_right > 15 and light_blue_two > 5 and light_blue > 5:
                    return "endround"

                if light_blue > 5 and dark_blue_right_three > 60:
                    return "endround"

                if dark_blue_right >= 2 and light_blue > 25:
                    return "endround"

                if dark_blue_right_two > 5 and light_blue > 40 and light_blue_two > 15:
                    return "endround"

                if white < 34:
                    if (dark_blue_right > 10 or dark_blue_right_two > 40) and (
                        light_blue >= 1 or light_blue_two >= 1 or light_blue_three >= 1
                    ):
                        return "endround"

                if dark_blue_right > 1500:
                    return "endround"

            is_endround_roi = self.frame[0:38, 195 : 195 + 356]

            dark_blue_left = vf_cv.CvHelper.count_pixels(
                "#1a2cd1", is_endround_roi, override_tolerance=10
            )
            dark_blue_right = vf_cv.CvHelper.count_pixels("#0e3e97", is_endround_roi)
            dark_blue_right_two = vf_cv.CvHelper.count_pixels(
                "#3f4d74", is_endround_roi, override_tolerance=5
            )

            dark_blue_right_three = vf_cv.CvHelper.count_pixels(
                "#44447b", is_endround_roi, override_tolerance=5
            )

            light_blue = vf_cv.CvHelper.count_pixels(
                "#999fe4", is_endround_roi, override_tolerance=10
            )
            light_blue_two = vf_cv.CvHelper.count_pixels(
                "#aaa0e8", is_endround_roi, override_tolerance=10
            )
            light_blue_three = vf_cv.CvHelper.count_pixels(
                "#92aaff", is_endround_roi, override_tolerance=10
            )

            maroon = vf_cv.CvHelper.count_pixels(
                "#693038", is_endround_roi, override_tolerance=5
            )

            if debug_time:
                cv2.imshow(
                    f"{dark_blue_left} {dark_blue_right} {dark_blue_right_two} {light_blue} {light_blue_two} {light_blue_three} mrn: {maroon} thr: {dark_blue_right_three}",
                    is_endround_roi,
                )
                cv2.waitKey()

            if maroon > 40 and light_blue > 10:
                return "endround"

            if maroon > 50 and light_blue_two > 40:
                return "endround"

            if maroon > 50 and dark_blue_right > 100:
                return "endround"

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
            if running_out:
                x = (int)(x + w / 2)
            roi = self.frame[y : y + h, x : x + w]

            blue_count = vf_cv.CvHelper.count_pixels("#5b1dc7", roi)

            if blue_count >= 5:
                return "endround"

            gray_image = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            self.rois[digit_num - 1] = roi

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
                    f"{self.thresholded_image.shape[1]} x {self.thresholded_image.shape[0]} :: {self.n_white_pix} :: {self.quads[7]} {self.quads[9]} {self.quads[1]} {self.quads[3]}",
                    self.thresholded_image,
                )
                cv2.imshow("original", roi)
                cv2.waitKey()

            if self.is_endround():
                return "endround"
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
                return "endround"
                # raise Exception("unrecognized digit")

            if running_out:
                return text

        if float(text) < 0:
            raise Exception(f"Found incorrect time {text}")

        if float(text) > 45:
            raise Exception(f"Found incorrect time {text}")

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
