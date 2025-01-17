"""This module gives information about a frame that shows a round being won"""

import cv2
import pytesseract
import vf_cv.cv_helper


class WinningFrame:
    """This class gives information about a frame that shows a round being won"""

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
        "to": (185, 204, 484, 80),
    }

    def set_frame(self, frame):
        """Sets the image to extract data from"""
        self.frame = frame
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
        elif self.frame_height == 720 and region_name != "to":
            (x, y, w, h) = self.REGIONS_480P[region_name]
            x = (int)(x * 1.5)
            y = (int)(y * 1.5)
            w = (int)(w * 1.5)
            h = (int)(h * 1.5)
        elif self.frame_height == 720 and region_name == "to":
            (x, y, w, h) = self.REGIONS_480P[region_name]
            x = (int)(x * 1.5)
            y = (int)(y * 1.5)
            w = (int)(w * 1.5)
            h = (int)(h * 1.5)

            y += 15
            h -= 40
            x += 75
            w -= 375
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

        w = 250

        roi = self.frame[y : y + h, x : x + w]

        green_count = vf_cv.CvHelper.count_pixels("#07a319", roi, override_tolerance=15)
        light_green = vf_cv.CvHelper.count_pixels("#91ff92", roi, override_tolerance=15)
        early_green = vf_cv.CvHelper.count_pixels("#72ff2d", roi, override_tolerance=15)

        red_tekken_count = 0
        roi_bw = None

        if debug:
            cv2.imshow(
                f"ro eg {early_green} g{green_count} red {red_tekken_count} light_green {light_green}",
                roi,
            )
            cv2.waitKey()

        if self.frame_height == 360:
            roi_bw = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            if roi_bw[27, 17] < 190:
                return False

            if roi_bw[26, 69] < 190:
                return False

            if roi_bw[26, 93] < 190:
                return False

            if light_green > 70 and green_count == 0:
                return False
            return green_count + light_green > 50
        elif self.frame_height == 1080:
            if early_green > 1000:
                return True

            if w == 250 and green_count > 50:
                return True
        elif self.frame_height == 720:
            if early_green > 665:
                return True

            if green_count > 50:
                return True

        return green_count + light_green > 300 or red_tekken_count > 2000

    def is_timeout(self, debug=False):
        region_name = "to"
        (x, y, w, h) = self.get_roi(region_name)

        roi = self.frame[y : y + h, x : x + w]

        roi_bw = vf_cv.CvHelper.prepare_green_text_for_ocr(roi)
        roi_bw = vf_cv.CvHelper.add_white_row(roi_bw, 10)
        roi_bw = vf_cv.CvHelper.add_white_column(roi_bw, 10)

        green_count = vf_cv.CvHelper.count_pixels("#07a319", roi, override_tolerance=15)
        light_green = vf_cv.CvHelper.count_pixels("#91ff92", roi, override_tolerance=15)
        red_tekken_count = vf_cv.CvHelper.count_pixels(
            "#e42e20", roi, override_tolerance=15
        )

        if green_count < 50:
            return False

        text = pytesseract.image_to_string(
            roi_bw, config="--psm 7 -c tessedit_char_whitelist=TIME\\ OUT"
        ).strip()

        if debug:
            cv2.imshow(
                f"ro g{green_count} red {red_tekken_count} light_green {light_green}",
                roi,
            )
            print(f"Timeout text [{text}]")
            cv2.imshow(f"ro bw {green_count} [{text}]", roi_bw)
            cv2.waitKey()

        return "TIME" in text

    def is_ko_endround(self, debug_ko=False):
        region_name = "ko"
        (x, y, w, h) = self.get_roi(region_name)

        roi = self.frame[y : y + h, x : x + w]
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        if debug_ko:
            debug_string = f"{self.frame_height} ko"
            cv2.imshow(
                debug_string,
                roi,
            )
            print(debug_string)
            cv2.resizeWindow(debug_string, 800, 400)
            cv2.waitKey()

    def is_ko(self, debug_ko=False):
        region_name = "ko"
        (x, y, w, h) = self.get_roi(region_name)

        roi = self.frame[y : y + h, x : x + w]
        roi_bw = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        if debug_ko:
            debug_string = f"{self.frame_height} ko"
            cv2.imshow(
                debug_string,
                roi_bw,
            )
            print(debug_string)
            cv2.resizeWindow(debug_string, 800, 400)
            cv2.waitKey()

        if self.frame_height == 360:
            if roi_bw[92, 9] > 80:
                return False
            if roi_bw[13, 82] > 60:
                return False
            if roi_bw[69, 23] < 235:
                return False
            if roi_bw[20, 80] < 200:
                return False
            return True

        gold_count = vf_cv.CvHelper.count_pixels("#ce9e54", roi, override_tolerance=5)
        purple_count = vf_cv.CvHelper.count_pixels(
            "#422fc9", roi, override_tolerance=25
        )
        black_count = vf_cv.CvHelper.count_pixels("#000000", roi, override_tolerance=25)
        white_count = vf_cv.CvHelper.count_pixels("#FFFFFF", roi, override_tolerance=25)
        red_tekken_count = vf_cv.CvHelper.count_pixels(
            "#e42e20", roi, override_tolerance=10
        )
        blue = vf_cv.CvHelper.count_pixels("#5c78ef", roi)
        brown_gold = vf_cv.CvHelper.count_pixels("#c98c38", roi, override_tolerance=5)

        if (
            self.frame_height == 480
            or self.frame_height == 720
            or self.frame_height == 1080
        ):
            if debug_ko:
                debug_string = f"{self.frame_height} ko bg {brown_gold} roi gold {gold_count} purple{purple_count} blue {blue} white {white_count} black{black_count}"
                cv2.imshow(
                    debug_string,
                    roi,
                )
                print(debug_string)
                cv2.resizeWindow(debug_string, 800, 400)
                cv2.waitKey()

            if blue > 1800 and self.frame_height != 1080:
                return False

            if (
                self.frame_height == 480
                and gold_count > 55
                and purple_count < 10
                and 15 <= blue <= 45
            ):
                return True

            if self.frame_height == 360:
                if gold_count >= 17 and blue >= 10 and black_count < 1000:
                    return True

                if (
                    5 <= brown_gold <= 18
                    and 10 <= gold_count <= 20
                    and 900 <= white_count <= 1100
                ):
                    return True

                if 90 <= brown_gold <= 110 and 7 <= gold_count <= 27:
                    return True

                if gold_count >= 2 and 45 <= black_count < 1000 and white_count >= 1000:
                    return True

                if gold_count > 10 and white_count > 7000:
                    return True
                if (
                    white_count > 200
                    and gold_count > 15
                    and purple_count > 30
                    and black_count < 5000
                ):
                    return True
                if gold_count > 42 and purple_count > 10 and white_count > 0:
                    return True
                if (
                    gold_count >= 25
                    and blue >= 20
                    and 125 <= white_count <= 275
                    and black_count < 2500
                ):
                    return True
            if self.frame_height == 480 and gold_count > 130 and blue < 20:
                return True

            if self.frame_height == 480 and purple_count > 140 and black_count > 200:
                return False

            if self.frame_height != 360:
                if gold_count > 10 and white_count > 7000:
                    return True
                if white_count > 15000:
                    return True
                if gold_count > 42 and purple_count > 10:
                    return True

                if (
                    red_tekken_count > 40
                    and red_tekken_count < 165
                    and black_count > 5000
                ):
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
        roi_bw = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        white_count = vf_cv.CvHelper.count_pixels("#ffffff", roi, override_tolerance=5)
        gold_count = vf_cv.CvHelper.count_pixels("#ce9e54", roi, override_tolerance=5)
        red_count = vf_cv.CvHelper.count_pixels("#b3200e", roi, override_tolerance=25)
        purple_count = vf_cv.CvHelper.count_pixels(
            "#422fc9", roi, override_tolerance=25
        )
        black_count = vf_cv.CvHelper.count_pixels("#000000", roi, override_tolerance=25)
        light_yellow = vf_cv.CvHelper.count_pixels("#f8ff7b", roi, override_tolerance=5)
        lg = vf_cv.CvHelper.count_pixels("#fbf2b6", roi, override_tolerance=5)
        if debug_excellent is True:
            debug_string = f"{self.frame_height} ex  w[{white_count}]_g[{gold_count}]_r[{red_count}]p[{purple_count}]_b[{black_count}]_ly[{light_yellow}]_lg[{lg}]"
            print(debug_string)
            cv2.imshow(debug_string, roi)
            cv2.imshow(f"excellent roi bw{lg}", roi_bw)

            cv2.waitKey()

        if self.frame_height == 360:
            if roi_bw[27, 31] < 200:
                return False

            if roi_bw[11, 174] < 180:
                return False

            if roi_bw[9, 362] < 180:
                return False

            if white_count > 375 and gold_count > 20 and black_count < 1390:
                return True

            if lg > 300 and gold_count > 5 and black_count < 1300:
                return True

            if lg > 120 and white_count > 20 and black_count < 1300:
                return True

        if self.frame_height == 1080:
            if white_count > 37000 and gold_count < 100 and black_count < 400:
                return True

            if white_count > 20000 and gold_count < 275 and black_count < 175:
                return True

            if black_count > 3500 and gold_count < 200 and white_count < 1000:
                return False

            if white_count > 3800 and gold_count > 250 and black_count < 100:
                return True

            if white_count > 5000 and light_yellow > 1200:
                return True

            if white_count > 1500 and gold_count > 775:
                return True

            if white_count > 8000 and gold_count > 200 and black_count < 100:
                return True

            if (
                white_count > 7250
                and gold_count > 70
                and red_count > 225
                and black_count < 75
            ):
                return True

            if white_count > 23000 and gold_count > 220 and black_count < 220:
                return True

        if (
            black_count > 2300
            and white_count < 15
            and red_count < 15
            and purple_count < 15
        ):
            return False

        if white_count < 10 and gold_count < 10:
            return False

        if self.frame_height == 720 and white_count < 10 and gold_count < 40:
            return False

        if self.frame_height == 720 and lg > 600:
            return True

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

        if debug_excellent:
            print(f"{self.frame_height}p excellent returning default false")

        return False

    def get_player_health(self, player_num):
        region_name = f"player{player_num}_health"
        (x, y, w, h) = self.get_roi(region_name)

        roi = self.frame[y : y + h, x : x + w]
        green_health = vf_cv.CvHelper.count_pixels("#30c90e", roi, override_tolerance=5)
        black_health = vf_cv.CvHelper.count_pixels("#1d1d1d", roi, override_tolerance=5)
        grey_health = vf_cv.CvHelper.count_pixels("#1c211d", roi, override_tolerance=5)

        return [green_health, black_health, grey_health]
