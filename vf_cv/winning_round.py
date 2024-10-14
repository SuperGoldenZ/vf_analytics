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

    def is_winning_round(self, debug_winning_round=False):
        region_name = "all_rounds"
        (x, y, w, h) = self.get_roi(region_name)

        roi = self.frame[y : y + h, x : x + w]

        maroon = vf_cv.CvHelper.count_pixels("#690003", roi, 10)
        if self.frame_height == 720 and maroon > 300:
            return 0

        maroon_2 = vf_cv.CvHelper.count_pixels("#75000f", roi, 10)
        if self.frame_height == 720 and maroon_2 > 300:
            return 0

        pink = vf_cv.CvHelper.count_pixels("#ed3c61", roi, 10)
        if self.frame_height == 720 and pink > 200:
            return 0

        if self.frame_height == 720 and pink > 75 and maroon > 15:
            return 0

        if self.frame_height == 720 and (pink > 35 and maroon > 150 and maroon_2 > 75):
            return 0

        if self.frame_height == 720 and (pink > 35 and maroon > 50 and maroon_2 > 150):
            return 0

        lr = vf_cv.CvHelper.count_pixels("#af0614", roi, 10)
        if self.frame_height == 720 and (lr > 150):
            return 0

        if self.frame_height == 720 and (lr > 50 and pink > 30):
            return 0

        dark_blue = vf_cv.CvHelper.count_pixels("#0000c8", roi, 20)
        if self.frame_height == 720 and dark_blue > 250:
            return 0

        darker_blue = vf_cv.CvHelper.count_pixels("#101e5e", roi, 5)
        if self.frame_height == 720 and darker_blue > 50:
            return 0

        if (
            self.frame_height == 720
            and darker_blue > 10
            and dark_blue > 100
            and pink > 50
            and maroon > 40
        ):
            return 0

        if (
            self.frame_height == 720
            and dark_blue > 10
            and pink > 50
            and maroon > 100
            and maroon_2 > 80
        ):
            return 0

        if self.frame_height == 720 and pink > 70 and maroon > 40 and maroon_2 > 40:
            return 0

        other_dark_blue = vf_cv.CvHelper.count_pixels("#1b2ff1", roi, 5)
        third_dark_blue = vf_cv.CvHelper.count_pixels("#1316f0", roi, 5)
        light_blue = vf_cv.CvHelper.count_pixels("#6e90ff", roi, 5)

        if debug_winning_round is True:
            cv2.imshow(
                f"lr {lr} drb {darker_blue} db {dark_blue} lr {lr} {self.frame_height}  other {other_dark_blue}  third {third_dark_blue} lb {light_blue} pink {pink} mr {maroon} m2 {maroon_2}",
                roi,
            )
            cv2.waitKey()

        if self.frame_height == 480 and lr > 85:
            return 0

        if self.frame_height == 1080 and (
            dark_blue + third_dark_blue + other_dark_blue + light_blue
        ) >= (15 + 16 + 10 + 85):
            return 0

        if self.frame_height == 480 and dark_blue > 70:
            return 0

        if self.frame_height == 1080 and dark_blue > 200:
            return 0

        if self.frame_height == 1080 and other_dark_blue >= 25:
            return 0

        if self.frame_height == 1080 and third_dark_blue >= 13:
            return 0

        bar_blue_two = vf_cv.CvHelper.count_pixels("#0636a5", roi, 5)
        if bar_blue_two >= 60:
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
            or all_dark_maroon >= 20
            or other_maroon > 80
            or other_db > 80
            or other_blue > 25
            or another_blue >= 15
            or bar_blue >= 10
            or more_blue > 7
        ):
            # print(f"return 480 {all_dark_blue} {all_dark_maroon} {other_maroon} {other_db} {all_dark_red} bb{bar_blue} mb {more_blue}")
            return 0

        for player_num in range(1, 3):
            region_name = f"player{player_num}_rounds"
            (x, y, w, h) = self.get_roi(region_name)
            roi = self.frame[y : y + h, x : x + w]

            # cv2.imshow("roi", roi)
            # cv2.waitKey()
            roi_bw = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            if player_num == 2:
                threshold = 5

                whiter_blue = vf_cv.CvHelper.count_pixels("#f1ffff", roi, threshold)
                white = vf_cv.CvHelper.count_pixels("#fFffff", roi, threshold)
                ob = vf_cv.CvHelper.count_pixels("#d9f4ff", roi, threshold)
                tblue = vf_cv.CvHelper.count_pixels("#64e1ee", roi, threshold)
                teal = vf_cv.CvHelper.count_pixels("#4ccafb", roi, threshold)
                aot = vf_cv.CvHelper.count_pixels("#88f6ff", roi, threshold)

                if debug_winning_round:
                    cv2.imshow(
                        f"aot {aot} w_b {whiter_blue}  w {white} ob {ob} tb {tblue} t {teal}",
                        roi,
                    )

                    cv2.imshow("roi bw player 2", roi_bw)

                    cv2.waitKey()

                if self.frame_height == 360:
                    if whiter_blue >= 2:
                        return player_num

                    if tblue + teal >= 5:
                        return player_num

                    if roi_bw[5, 21] > 150:
                        return player_num

                    if roi_bw[5, 35] > 150:
                        return player_num

                    if roi_bw[5, 48] > 150:
                        return player_num

                if self.frame_height == 480 and 20 <= ob <= 40:
                    return player_num

                if 45 <= whiter_blue <= 85:
                    return player_num

                if self.frame_height == 360 and aot > 5:
                    return 2

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

            if player_num == 1:
                threshold = 5
                # if self.frame_height == 360:
                # threshold=15

                op = vf_cv.CvHelper.count_pixels("#fee5f0", roi, threshold)
                other_pink = vf_cv.CvHelper.count_pixels("#f25f71", roi, threshold)
                opp = vf_cv.CvHelper.count_pixels("#ffa8a9", roi, threshold)
                pr = vf_cv.CvHelper.count_pixels("#fd486c", roi, threshold)
                anp = vf_cv.CvHelper.count_pixels("#ff7a89", roi, threshold)
                # if self.frame_height == 360:
                # anp = vf_cv.CvHelper.count_pixels("#ff7a89", roi, 15)
                pf = vf_cv.CvHelper.count_pixels("#f0788a", roi, threshold)

                if debug_winning_round:
                    cv2.imshow(
                        f"pf {pf} {anp} {opp} {other_pink} <- op -> {op} wrc{white_red_count}  wc{white_count} pc {pink_count} {light_blue_count} lbc pr {pr}",
                        roi,
                    )
                    cv2.imshow("roi bw player 1", roi_bw)
                    cv2.waitKey()

                if self.frame_height == 1080:
                    if op > 15:
                        return player_num
                else:
                    if op > 5:
                        return player_num
                if white_red_count >= 15:
                    return player_num

                if self.frame_height == 480 and other_pink >= 3 and op >= 1:
                    return player_num

                if self.frame_height == 720 and 15 <= other_pink <= 25:
                    return player_num

                if self.frame_height == 720 and 15 <= opp <= 25:
                    return player_num

                if (
                    self.frame_height == 360
                    and white_red_count >= 10
                    and white_count >= 4
                ):
                    return player_num

                # player1 B&W
                if self.frame_height == 360:
                    if 120 < roi_bw[6, 33] < 140:
                        return player_num

                    if 120 < roi_bw[6, 21] < 140:
                        return player_num

                    if roi_bw[6, 21] > 200:
                        return player_num

                    if roi_bw[6, 33] > 200:
                        return player_num

                    if roi_bw[6, 6] > 200:
                        return player_num

                    if pf >= 1 and anp >= 1 and opp >= 1:
                        return player_num

                    if anp > 5:
                        return player_num

                    if pf >= 5:
                        return player_num

                    if pr > 5:
                        return player_num

                    if opp > 5:
                        return player_num

            if 20 <= white_count <= 30 and pink_count == 0:
                return player_num

            if (
                white_count > 8
                or (pink_count >= 5 and player_num == 1)
                or light_blue_count >= 5
            ) and (grey_count < 50):
                return player_num

        return 0
