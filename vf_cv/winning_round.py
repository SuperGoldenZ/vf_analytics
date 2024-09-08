"""This module gives information about a frame that shows a round being won"""

import cv2
import vf_cv.cv_helper


class WinningRound:
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

    def is_winning_round(self, debug_winning_round=False):
        region_name = "all_rounds"
        (x, y, w, h) = self.get_roi(region_name)

        factor = 1.0

        if self.frame_height == 720:
            factor = 1.5

        x = int(x * factor)
        y = int(y * factor)
        w = int(w * factor)
        h = int(h * factor)

        roi = self.frame[y : y + h, x : x + w]
        dark_blue = vf_cv.CvHelper.count_pixels("#0000c8", roi, 20)
        other_dark_blue = vf_cv.CvHelper.count_pixels("#1b2ff1", roi, 5)
        third_dark_blue = vf_cv.CvHelper.count_pixels("#1316f0", roi, 5)

        # if debug_winning_round is True:
        # cv2.imshow(f"roi dark blue {dark_blue}   {self.frame_height}  other {other_dark_blue}  third {third_dark_blue}", roi)
        # cv2.waitKey()

        if self.frame_height == 480 and dark_blue > 70:
            return 0

        if self.frame_height == 1080 and dark_blue > 200:
            return 0

        if self.frame_height == 1080 and other_dark_blue >= 25:
            return 0

        if self.frame_height == 1080 and third_dark_blue >= 13:
            return 0

        bar_blue_two = vf_cv.CvHelper.count_pixels("#0636a5", roi, 5)
        if bar_blue_two >= 60 * factor:
            return 0

        teal = vf_cv.CvHelper.count_pixels("#68fffe", roi, 5)
        if teal > 15:
            return 0

        all_dark_red = vf_cv.CvHelper.count_pixels("#780103", roi, 5)
        all_dark_maroon = vf_cv.CvHelper.count_pixels("#520004", roi, 5)
        other_blue = vf_cv.CvHelper.count_pixels("#36539f", roi, 5)
        another_blue = vf_cv.CvHelper.count_pixels("#213275", roi, 1)
        other_db = vf_cv.CvHelper.count_pixels("#1e00b3", roi, 5)
        other_maroon = vf_cv.CvHelper.count_pixels("#691f34", roi, 5)
        bar_blue = vf_cv.CvHelper.count_pixels("#0318c6", roi, 5)
        all_dark_blue = vf_cv.CvHelper.count_pixels("#03176d", roi, 5)
        more_blue = vf_cv.CvHelper.count_pixels("#443fe7", roi, 5)

        if self.frame_height == 480 and (
            all_dark_blue >= 5
            or all_dark_red >= 5
            or all_dark_maroon >= 10
            or other_maroon > 80
            or other_db > 80
            or other_blue > 25
            or another_blue >= 15
            or bar_blue >= 10
            or more_blue > 7
        ):
            # print ("arbot a")
            return 0

        # if (all_dark_blue >= 5*factor or all_dark_red >= 5 or all_dark_maroon >= 10 or other_maroon > 80 or other_db > 80 or other_blue > 25 or another_blue >= 10 or bar_blue >= 10 or more_blue > 7):
        # return 0

        for player_num in range(1, 3):
            region_name = f"player{player_num}_rounds"
            (x, y, w, h) = self.get_roi(region_name)
            roi = self.frame[y : y + h, x : x + w]

            # cv2.imshow("roi", roi)
            # cv2.waitKey()

            if player_num == 2:
                whiter_blue = vf_cv.CvHelper.count_pixels("#f1ffff", roi, 5)
                if 45 <= whiter_blue <= 85:
                    return player_num

                another_teal = vf_cv.CvHelper.count_pixels("#a8ffff", roi, 5)
                if 25 <= another_teal <= 28:
                    return player_num

                teal = vf_cv.CvHelper.count_pixels("#77f8fe", roi, 5)
                if 5 <= teal <= 15:
                    return player_num

                light_teal = vf_cv.CvHelper.count_pixels("#d1fdff", roi, 5)
                if 10 <= light_teal <= 25:
                    return player_num

                white_blue_count = vf_cv.CvHelper.count_pixels("#e4feff", roi, 5)
                if white_blue_count > 20:
                    return player_num

            dark_blue = vf_cv.CvHelper.count_pixels("#03176d", roi, 5)
            dark_red = vf_cv.CvHelper.count_pixels("#780103", roi, 5)
            if dark_red > 50 or dark_blue > 50:
                return 0

            off_white_count = vf_cv.CvHelper.count_pixels("#f9fff2", roi, 5)
            if off_white_count > 15:
                return player_num

            white_count = vf_cv.CvHelper.count_pixels("#ffffff", roi, 5)
            white_red_count = vf_cv.CvHelper.count_pixels("#fff5ee", roi, 4)
            pink_count = vf_cv.CvHelper.count_pixels("#f6d8be", roi, 5)
            light_blue_count = vf_cv.CvHelper.count_pixels("#71fffe", roi, 5)
            grey_count = vf_cv.CvHelper.count_pixels("#aaaaac", roi, 5)

            # print(f"white count {white_count} wrc {white_red_count}")
            # print(f"white count {white_count} pink {pink_count} blue {light_blue_count} dr {dark_red} db {dark_blue} off {off_white_count} wb {white_blue_count} teal {teal} lightteal {light_teal} at {another_teal} whiterblue {whiter_blue}")

            if player_num == 1:
                op = vf_cv.CvHelper.count_pixels("#fee5f0", roi, 5)
                if op > 5:
                    return player_num
                if white_red_count >= 15:
                    return player_num
            if 20 <= white_count <= 30 and pink_count == 0:
                return player_num

            if (
                white_count > 8
                or (pink_count >= 5 and player_num == 1)
                or light_blue_count >= 5
            ) and (grey_count < 50):
                # print(f"got winning rounds white count {white_count} pink {pink_count} blue {light_blue_count} dr {dark_red} db {dark_blue} all_maroon {all_dark_maroon} all dark red {all_dark_red} all_dark_blue {all_dark_blue} grey {grey_count}")
                # cv2.imshow(f"roi for winner {player_num}", roi)
                # cv2.waitKey()

                return player_num

        return 0
