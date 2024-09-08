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
    }

    frame = None
    frame_height = None

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

        if self.frame_height == 720:
            factor = 1.5

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

            if contours:
                x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
                thresholded_image = thresholded_image[y : y + h, x : x + w]

                height, width = (
                    thresholded_image.shape
                )  # Get the dimensions of the frame
                n_white_pix = 0

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
                        x, y, w, h = cv2.boundingRect(
                            max(contours, key=cv2.contourArea)
                        )
                        thresholded_image = thresholded_image[y : y + h, x : x + w]

                    height, width = (
                        thresholded_image.shape
                    )  # Get the dimensions of the frame

                    digit, n_white_pix = Timer.get_time_ms_digit_1080(
                        thresholded_image, width, height
                    )
                    text = f"{text}{digit}"

                    if debug:
                        cv2.imshow(f"roi", roi)
                        cv2.imshow(f"gray", gray_image)
                        cv2.imshow(
                            f"threshold 1080 {n_white_pix}   height {height}  width {width}",
                            thresholded_image,
                        )
                        cv2.waitKey()

            if self.frame_height == 720:
                n_white_pix = np.sum(thresholded_image == 255)

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

    def is_time_running_out(self, debug=False):
        """Returns true if last 10 seconds of a round"""

        region_name = "time_seconds_digit1"
        (x, y, w, h) = self.get_roi(region_name)
        roi = self.frame[y : y + h, x : x + w]

        count = vf_cv.CvHelper.count_pixels("#FF0000", roi)

        if debug:
            cv2.imshow(f"roi {count}", roi)
            cv2.waitKey()

        threshold = 100
        if h == 480:
            threshold = 50

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

    def get_time_seconds_digit_1080p(self, gray_image, digit_num, debug_time=False):
        thresholded_image = Timer.get_thresholded_image(gray_image, 200)

        height, width = thresholded_image.shape  # Get the dimensions of the frame

        n_white_pix_1080 = np.sum(thresholded_image == 255)
        if debug_time is True:
            cv2.imshow("grey", gray_image)
            cv2.imshow(
                f"threshold height {self.frame_height} {n_white_pix_1080}  width {width}",
                thresholded_image,
            )
            cv2.waitKey()

        upper_right = thresholded_image[0, width - 2]

        if 1335 <= n_white_pix_1080 < 1355 and 45 <= width <= 50 and upper_right == 0:
            return 2
        elif 1245 <= n_white_pix_1080 < 1270 and 45 <= width <= 50 and upper_right == 0:
            return 2
        elif n_white_pix_1080 < 900 and width <= 35:
            return 1
        elif n_white_pix_1080 == 1523 and width == 46:
            return 9
        elif 1545 - 10 <= n_white_pix_1080 <= 1545 + 10:
            return 8
        elif 1388 - 10 <= n_white_pix_1080 <= 1398 + 10:
            return 5
        elif n_white_pix_1080 == 1264:
            return 2
        else:
            digit = self.get_time_digit(thresholded_image, width, height, digit_num)
            return digit

    def get_time_seconds(self, debug_time=False):
        """Returns number of seconds remaining in a round"""

        text = ""

        factor = 1.0

        if self.frame_height == 720:
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

            running_out = self.is_time_running_out()
            if running_out:
                x = (int)(x + w / 2)
            roi = self.frame[y : y + h, x : x + w]

            gray_image = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            n_white_pix = 0
            if self.frame_height == 1080:
                digit = self.get_time_seconds_digit_1080p(
                    gray_image, digit_num, debug_time=debug_time
                )
                text = f"{text}{digit}"
                if running_out:
                    return text
            else:
                thresholded_image = Timer.get_thresholded_image(gray_image, 200)
                height, width = (
                    thresholded_image.shape
                )  # Get the dimensions of the frame

                if self.frame_height == 720:
                    digit = self.get_time_digit(
                        thresholded_image, width, height, digit_num
                    )
                    text = f"{text}{digit}"
                    if running_out:
                        return text
                else:
                    n_white_pix = np.sum(thresholded_image == 255)

            if n_white_pix <= 175 * factor and n_white_pix > 10 * factor:
                text = f"{text}1"
            elif (
                226 * factor <= n_white_pix <= 253 * factor
                or ((264 - 10) * factor <= n_white_pix <= 264 * factor)
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

                height, width = (
                    thresholded_image.shape
                )  # Get the dimensions of the frame
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

                if (
                    middle == 0
                    and upper_right == 0
                    and lowerleft == 0
                    and veryupperleft == 0
                    and lower_right == 0
                    and midleftquarter != 0
                    and top_middle != 0
                ):
                    text = f"{text}0"
                elif bottom_middle == 0 and left_quarter != 0 and midleft != 0:
                    text = f"{text}6"
                elif (
                    lower_right == 0
                    and lowerleft == 0
                    and lowerleft2 == 0
                    and upper_right == 0
                    and veryupperleft == 0
                    and midleft == 0
                    and midleftquarter == 0
                ):
                    text = f"{text}3"
                elif upper_right == 0 and color != 0:
                    text = f"{text}9"
                elif (
                    upperleft != 0
                    and lowerleft == 0
                    and upper_right != 0
                    and digit_num == 2
                ):
                    text = f"{text}5"
                elif upper_right != 0 and top_middle != 0 and digit_num == 2:
                    text = f"{text}5"
                elif color == 0 and lowerleft2 == 0:
                    text = f"{text}4"
                else:
                    text = f"{text}2"
            elif n_white_pix == 252:
                color = thresholded_image[10, 5]
                thresholded_image[10, 5] = 100

                # print(repr(color))
                # print(f"seconds n_white {n_white_pix}")
                # cv2.imshow("grey", thresholded_image)
                # cv2.waitKey()

                # print(f"rgb {r} {g} {b}")
                if color == 0:
                    text = f"{text}2"
                else:
                    text = f"{text}5"
            elif n_white_pix >= 278 - 5:
                height, width = (
                    thresholded_image.shape
                )  # Get the dimensions of the frame
                middle = thresholded_image[int(height / 2), int(width / 2)]
                middle2 = thresholded_image[int(height / 2) - 1, int(width / 2)]
                midleft = thresholded_image[int(height / 2), 0]
                upper_right = thresholded_image[int(height * 0.25), 0]

                # cv2.imshow("thresh", thresholded_image)
                # cv2.waitKey()

                if middle == 0 and middle2 == 0 and upper_right == 0:
                    text = f"{text}0"
                elif midleft != 0:
                    text = f"{text}6"
                else:
                    text = f"{text}8"
            elif (
                n_white_pix == 231
                or n_white_pix == 228
                or n_white_pix == 230
                or n_white_pix == 233
            ):
                text = f"{text}3"
            elif n_white_pix == 169:
                text = f"{text}1"
            elif 194 - 5 <= n_white_pix <= 194 + 5:
                text = f"{text}7"

        # if float(text) < 0:
        # raise Exception(f"Found incorrect time {text}")

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
    def get_time_digit(thresholded_image, width, height, digit_num, debug=False):
        """Returns one digit of the time remaining in a match"""

        if debug:
            cv2.imshow("thresholded_image", thresholded_image)
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

        try:
            points[244] = thresholded_image[24, 4]
            points["above_five"] = thresholded_image[
                int(height / 2) - 2, int(width / 2)
            ]
        except:
            return "00.00"

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
            and points[244] != 0
        ):
            return 8
        elif (
            points[5] != 0
            and points[4] == 0
            and points[4.5] != 0
            and points[5.5] != 0
            and points[57] != 0
            and points[59] != 0
        ):
            return 9
        elif (
            points[5] != 0
            and points[7] == 0
            and points[1] == 0
            and points[9] == 0
            and points[3] == 0
            and points[5.5] != 0
            and points[4.5] != 0
        ):
            return 6
        elif (
            points["above_five"] != 0
            and points[7] == 0
            and points[1] == 0
            and points[9] == 0
            and points[3] == 0
            and points[5.5] != 0
            and points[4.5] != 0
        ):
            return 6
        elif (
            points[9] != 0
            and points[5] == 0
            and points[2] != 0
            and points[7] == 0
            and points[1] == 0
        ) and points[59] == 0:
            return 5
        elif points[9] != 0 and points[5] == 0:
            return 4
        elif points[5] == 0 and points[4.5] != 0 and points[5.5] != 0:
            return 0
        elif (
            points[5] != 0
            and points[8] != 0
            and points[2] != 0
            and points[9] == 0
            and points[7] == 0
            and points[1] == 0
            and points[3] == 0
            and points[6] == 0
            and points[57] != 0
            and points[4.5] == 0
        ):
            return 3
        elif (
            points[5] != 0
            and points[2] != 0
            and points[9] == 0
            and points[7] == 0
            and points[1] == 0
            and points[3] == 0
            and points[6] == 0
            and points[57] != 0
            and points[4.5] == 0
        ):
            return 3
        elif (
            # points[5] == 0
            points[2] != 0
            and points[9] == 0
            and points[7] == 0
            and points[1] != 0
            and points[3] == 0
        ):
            return 2
        elif points[5] != 0 and points[8] != 0 and points[2] == 0 and points[1.5] != 0:
            return 7
        elif points[9] != 0 and points[5] != 0:
            return 1
        elif points[5] != 0:
            if digit_num == 1:
                return 3
            else:
                return 9

        return -1
