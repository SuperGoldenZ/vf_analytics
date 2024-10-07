"""This module gives information about a frame that shows a round being won"""

import cv2
import vf_cv.cv_helper


class WinningFrame:
    frame = None
    frame_height = None

    REGIONS_480P = {
        "player1_rounds": (307, 50, 55, 15),
        "player2_rounds": (475, 50, 80, 15),
        "player1_health": (111, 33, 265, 8),
        "player2_health": (483, 36, 265, 8),
        "stage": (342, 295, 200, 25),
        "player1ringname": (43, 315, 209, 18),
        "player2ringname": (589, 315, 209, 18),
        "player1character": (35, 228, 245, 32),
        "player2character": (584, 228, 245, 32),
        "all_rounds": (247, 45, 404, 31),
        "vs": (343, 173, 172, 85),
        "ko": (250, 170, 350, 140),
        "excellent": (75, 200, 700, 80),
        "ro": (185, 204, 484, 80),
    }

    def set_frame(self, frame):
        """Sets the image to extract data from"""
        self.frame = frame
        self.frame_height = frame.shape[0]

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

    def is_ringout(self, debug=False):
        region_name = "ro"
        (x, y, w, h) = self.get_roi(region_name)

        roi = self.frame[y : y + h, x : x + w]

        green_count = vf_cv.CvHelper.count_pixels("#07a319", roi, override_tolerance=15)
        light_green = vf_cv.CvHelper.count_pixels("#91ff92", roi, override_tolerance=15)
        red_tekken_count = vf_cv.CvHelper.count_pixels(
            "#e42e20", roi, override_tolerance=15
        )

        if debug:
            cv2.imshow("roi", roi)
            print(
                f"green {green_count}  red {red_tekken_count}  light_green {light_green}"
            )
            print(green_count > 300 or red_tekken_count > 2000)
            cv2.waitKey()
        return green_count + light_green > 300 or red_tekken_count > 2000

    def is_ko(self, debug_ko=False):
        region_name = "ko"
        (x, y, w, h) = self.get_roi(region_name)

        roi = self.frame[y : y + h, x : x + w]

        gold_count = vf_cv.CvHelper.count_pixels("#ce9e54", roi, override_tolerance=5)
        # red_count = vf_cv.CvHelper.count_pixels("#b3200e", roi, override_tolerance=25)
        purple_count = vf_cv.CvHelper.count_pixels(
            "#422fc9", roi, override_tolerance=25
        )
        black_count = vf_cv.CvHelper.count_pixels("#000000", roi, override_tolerance=25)
        white_count = vf_cv.CvHelper.count_pixels("#FFFFFF", roi, override_tolerance=25)
        red_tekken_count = vf_cv.CvHelper.count_pixels(
            "#e42e20", roi, override_tolerance=10
        )
        blue = vf_cv.CvHelper.count_pixels("#5c78ef", roi)

        # ko count gold 144 red 135 purple91 black 484 white 766 resolution 480p tekken red 3
        if (
            self.frame_height == 360
            or self.frame_height == 480
            or self.frame_height == 720
            or self.frame_height == 1080
        ):
            if debug_ko:
                cv2.imshow(
                    f"{self.frame_height} ko roi gold {gold_count} purple{purple_count} blue {blue} white {white_count} black{black_count}",
                    roi,
                )
                cv2.waitKey()

            if blue > 1800:
                return False

            if (
                self.frame_height == 480
                and gold_count > 55
                and purple_count < 10
                and 15 <= blue <= 45
            ):
                return True

            if self.frame_height == 360 and gold_count >= 24 and blue >= 10:
                return True

            if self.frame_height == 480 and gold_count > 130 and blue < 20:
                return True

            if self.frame_height == 480 and purple_count > 140 and black_count > 200:
                return False
            if gold_count > 10 and white_count > 7000:
                return True
            if white_count > 15000:
                return True
            if gold_count > 42 and purple_count > 10:
                return True

            if red_tekken_count > 40 and red_tekken_count < 165 and black_count > 5000:
                return True

        return False

    def is_excellent(self, debug_excellent=False):
        (p1green, p1black, p1grey) = self.get_player_health(1)
        (p2green, p2black, p2grey) = self.get_player_health(2)

        p1excellent = p1black <= 2 and p1grey <= 2
        p2excellent = p2black <= 2 and p2grey <= 2

        if not p1excellent and not p2excellent:
            return False

        region_name = "excellent"
        (x, y, w, h) = self.get_roi(region_name)

        roi = self.frame[y : y + h, x : x + w]

        white_count = vf_cv.CvHelper.count_pixels("#ffffff", roi, override_tolerance=5)
        gold_count = vf_cv.CvHelper.count_pixels("#ce9e54", roi, override_tolerance=5)
        red_count = vf_cv.CvHelper.count_pixels("#b3200e", roi, override_tolerance=25)
        purple_count = vf_cv.CvHelper.count_pixels(
            "#422fc9", roi, override_tolerance=25
        )
        black_count = vf_cv.CvHelper.count_pixels("#000000", roi, override_tolerance=25)
        light_yellow = vf_cv.CvHelper.count_pixels("#f8ff7b", roi, override_tolerance=5)

        if debug_excellent is True:
            cv2.imshow(
                f"{self.frame_height} excellent roi white {white_count} gold {gold_count} red {red_count} purple {purple_count} black {black_count} light yelllow {light_yellow}",
                roi,
            )
            cv2.waitKey()

        if (
            self.frame_height == 1080
            and black_count > 3500
            and gold_count < 200
            and white_count < 1000
        ):
            return False

        if (
            self.frame_height == 1080
            and white_count > 3800
            and gold_count > 250
            and black_count < 100
        ):
            return True

        if self.frame_height == 1080 and white_count > 5000 and light_yellow > 1200:
            return True

        if (
            self.frame_height == 1080
            and white_count > 1500
            and gold_count > 775
            # and red_count > 500
            # and black_count < 1300
        ):
            return True

        if (
            self.frame_height == 1080
            and white_count > 8000
            and gold_count > 200
            and black_count < 100
        ):
            return True

        if (
            self.frame_height == 1080
            and white_count > 7250
            and gold_count > 70
            and red_count > 225
            and black_count < 75
        ):
            return True

        if (
            self.frame_height == 1080
            and white_count > 30000
            and gold_count > 50
            and black_count < 220
        ):
            return True

        if (
            black_count > 2300
            and white_count < 15
            and red_count < 15
            and purple_count < 15
        ):
            return False

        if white_count < 10 and gold_count < 10:
            # print ("2.5  false")
            return False

        if self.frame_height == 720 and white_count < 10 and gold_count < 40:
            return False

        if self.frame_height == 480:
            if 150 <= white_count <= 175 and 100 <= gold_count <= 120:
                return True

            if 1000 <= white_count <= 1250 and 65 <= gold_count <= 100:
                return True

            if 700 <= white_count <= 850 and 20 <= gold_count <= 30:
                return True

            if 575 <= white_count <= 625 and 10 <= gold_count <= 20:
                return True

            if 575 <= white_count <= 625 and 10 <= gold_count <= 20:
                return True

            if 175 <= white_count <= 200 and 100 <= gold_count <= 145:
                return True

            if 250 <= white_count <= 300 and 50 <= gold_count <= 100:
                return True

            if 140 < gold_count < 550 and red_count < 700 and 250 < black_count < 3500:
                return True

            if 215 - 10 <= white_count <= 215 + 10 and 50 <= gold_count <= 100:
                return True

            if 215 - 50 <= white_count <= 215 - 50 and 75 <= gold_count <= 125:
                return True

            if 476 - 50 <= white_count <= 476 + 50 and 28 <= gold_count <= 48:
                return True

        if self.frame_height == 1080:
            if white_count > 7901 - 10 and gold_count > 400 and black_count < 100:
                return True

        # return (
        # black_count > 900
        # and white_count < 150
        # and red_count < 100
        # and purple_count < 120
        # )

        return False

    def get_player_health(self, player_num):
        region_name = f"player{player_num}_health"
        (x, y, w, h) = self.get_roi(region_name)

        roi = self.frame[y : y + h, x : x + w]
        green_health = vf_cv.CvHelper.count_pixels("#30c90e", roi, override_tolerance=5)
        black_health = vf_cv.CvHelper.count_pixels("#1d1d1d", roi, override_tolerance=5)
        grey_health = vf_cv.CvHelper.count_pixels("#1c211d", roi, override_tolerance=5)

        return [green_health, black_health, grey_health]
