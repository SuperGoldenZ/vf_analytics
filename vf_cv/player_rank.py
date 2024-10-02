import vf_cv.cv_helper
import cv2
import pytesseract
import re
import numpy as np


class PlayerRank:
    REGIONS_480P = {
        "player1rank": (72, 91, 14, 12),
        "player1rank_full": (23, 82, 67, 21),
        "player2rank": (820, 91, 14, 12),
        "player2rank_full": (765, 82, 67, 21),
    }

    REGIONS_720P = {
        "player1rank": (108, 137, 21, 18),
        "player1rank_full": (
            int(23 * 1.5) - 10,
            int(82 * 1.5) - 6,
            int(67 * 1.5) + 10,
            int(21 * 1.5) + 6,
        ),
        "player2rank": (1230, 137, 21, 18),
        "player2rank_full": (
            int(765 * 1.5) - 3,
            int(82 * 1.5) - 6,
            int(67 * 1.5) + 10,
            int(21 * 1.5) + 6,
        ),
    }

    # REGIONS_720P = {
    # "player1rank": (72*1.5, 91*1.5, 14*1.5, 12*1.5),
    # "player1rank_full": (23*1.5, 82*1.5, 165, 55),
    # "player2rank": (820*1.5, 91*1.5, 14*1.5, 12*1.5),
    # "player2rank_full": (1718, 80, 165, 55),
    # }

    frame = None
    frame_height = None

    def __init__(self):
        self.rank_images = {
            37: cv2.imread("assets/test_images/480p/rank/37.jpg"),
            43: cv2.imread("assets/test_images/480p/rank/43.jpg"),
            44: cv2.imread("assets/test_images/480p/rank/44.jpg"),
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
            (x, y, w, h) = self.REGIONS_720P[region_name]
        elif self.frame_height == 1080:
            (x, y, w, h) = self.REGIONS_480P[region_name]
            x = (int)(x * 2.25)
            y = (int)(y * 2.25)
            w = (int)(w * 2.25)
            h = (int)(h * 2.25) - 10
        return (x, y, w, h)

    # min width 25
    def get_player_rank(self, player_num, debug_player_rank=False):
        FULL_REGION = f"player{player_num}rank_full"
        FULL_REGION_ROI = self.get_roi(FULL_REGION)

        REGULAR_REGION = f"player{player_num}rank"
        REGULAR_REGION_ROI = self.get_roi(REGULAR_REGION)

        (full_x, full_y, full_w, full_h) = FULL_REGION_ROI

        full_roi = self.frame[full_y : full_y + full_h, full_x : full_x + full_w]

        white_count = vf_cv.CvHelper.count_pixels("#000000", full_roi, 50)
        purple_count = vf_cv.CvHelper.count_pixels("#7600b9", full_roi)
        grey = vf_cv.CvHelper.count_pixels("#908f95", full_roi)
        dark_purple_count = vf_cv.CvHelper.count_pixels("#3a165e", full_roi)
        teal_count = vf_cv.CvHelper.count_pixels("#558784", full_roi)
        grellow_count = vf_cv.CvHelper.count_pixels("#8e9a52", full_roi)
        gold_count = vf_cv.CvHelper.count_pixels("#e2cb87", full_roi)
        ry = vf_cv.CvHelper.count_pixels("#cc5b31", full_roi)
        black_count = vf_cv.CvHelper.count_pixels("#000000", full_roi, 5)

        if debug_player_rank:
            cv2.imshow(
                f"{self.frame_height} gre{grellow_count} ry {ry} wc {white_count} grey {grey} dp {dark_purple_count}",
                full_roi,
            )
            cv2.waitKey()

        if self.frame_height == 1080:
            if (
                600 <= grellow_count <= 660
                and ry <= 20
                and 1200 <= white_count <= 1340
                and 950 <= grey <= 1280
            ):
                return 41

            if (
                442 - 10 <= grellow_count <= 459 + 10
                and ry <= 50
                and 1252 - 10 <= white_count <= 1252 + 10
                and 554 - 10 <= grey <= 667
                and 312 <= dark_purple_count <= 332
            ):
                return 41

            if (
                178 <= grellow_count <= 198
                and ry <= 5
                and 1860 <= white_count <= 1890
                and 1250 <= grey <= 1280
            ):
                return 40

            if (
                178 <= grellow_count <= 198
                and ry <= 5
                and 1860 <= white_count <= 1890
                and 1250 <= grey <= 1280
            ):
                return 40

            if (
                82 <= grellow_count <= 82
                and ry <= 135
                and 1198 <= white_count <= 1198
                and 204 - 10 <= grey <= 204 + 10
                and 549 - 10 <= dark_purple_count <= 549 + 10
            ):
                return 42

        if (
            self.frame_height == 480
            and 25 <= grellow_count <= 35
            and ry == 0
            and 350 <= white_count <= 370
            and 240 <= grey <= 260
        ):
            return 40

        if (
            self.frame_height == 480
            and 96 <= grellow_count <= 116
            and ry == 0
            and white_count <= 20
            and 540 <= grey <= 560
            and dark_purple_count > 170
        ):
            return 39

        if (
            self.frame_height == 720
            and 500 <= grellow_count <= 760
            and ry < 20
            and 430 <= white_count <= 660
            and 500 <= grey <= 980
            and 130 <= dark_purple_count <= 190
        ):
            return 41

        if (
            self.frame_height == 720
            and 507 - 10 <= grellow_count <= 507 + 10
            and ry < 15
            and 648 - 10 <= white_count <= 648 + 10
            and 570 - 10 <= grey <= 570 + 10
            and dark_purple_count > 25
        ):
            return 41

        if (
            self.frame_height == 720
            and 444 - 10 <= grellow_count <= 444 + 10
            and ry < 15
            and 1011 - 10 <= white_count <= 1011 + 10
            and 524 - 10 <= grey <= 524 + 10
            and dark_purple_count > 125
        ):
            return 41

        if (
            self.frame_height == 720
            and 444 - 10 <= grellow_count <= 1200 + 10
            and ry < 15
            and 600 - 10 <= white_count <= 1011 + 10
            and 524 - 10 <= grey <= 650 + 10
            and dark_purple_count > 125
        ):
            return 41

        if (
            self.frame_height == 720
            and 400 - 10 <= grellow_count <= 457 + 10
            and ry < 20
            and 800 - 10 <= white_count <= 1100 + 10
            and 500 - 10 <= grey <= 575 + 10
            and dark_purple_count > 125
        ):
            return 41

        if (
            self.frame_height == 720
            and 215 <= grellow_count <= 225
            and ry > 700
            and white_count > 1000
            and 178 <= grey <= 198
        ):
            return 43

        if (
            self.frame_height == 720
            and 435 <= grellow_count <= 435
            and 420 <= ry <= 460
            and 220 <= white_count <= 260
            and 160 <= grey <= 180
            and dark_purple_count < 20
        ):
            return 43

        if (
            self.frame_height == 720
            and 401 - 10 <= grellow_count <= 401 + 10
            and 435 - 10 < ry < 435 + 10
            and 262 - 10 <= white_count <= 262 + 10
            and 116 - 10 <= grey <= 116 + 10
            and dark_purple_count < 15
        ):
            return 43

        if (
            self.frame_height == 720
            and 427 - 10 <= grellow_count <= 427 + 10
            and 91 - 10 < ry < 91 + 10
            and 896 - 10 <= white_count <= 896 + 10
            and 156 - 10 <= grey <= 156 + 10
            and dark_purple_count < 30
        ):
            return 44

        if (
            self.frame_height == 720
            and 557 - 10 <= grellow_count <= 557 + 10
            and 91 - 10 < ry < 91 + 10
            and 245 - 10 <= white_count <= 245 + 10
            and 273 - 10 <= grey <= 273 + 10
            and dark_purple_count < 30
        ):
            return 44

        if (
            self.frame_height == 720
            and 577 - 10 <= grellow_count <= 637 + 10
            and 88 - 10 < ry < 97 + 10
            and 353 - 10 <= white_count <= 447 + 10
            and 223 - 10 <= grey <= 223 + 10
            and dark_purple_count < 30
        ):
            return 44

        if (
            self.frame_height == 720
            and 486 - 10 <= grellow_count <= 486 + 10
            and 119 - 10 < ry < 119 + 10
            and 327 - 10 <= white_count <= 327 + 10
            and 165 - 10 <= grey <= 165 + 10
            and dark_purple_count < 15
        ):
            return 44

        if (
            self.frame_height == 720
            and 281 - 10 <= grellow_count <= 281 + 10
            and 71 - 10 < ry < 71 + 10
            and 1384 <= white_count <= 1394 + 10
            and 93 <= grey <= 113
            and dark_purple_count < 25
        ):
            return 44

        if (
            self.frame_height == 720
            and 300 - 10 <= grellow_count <= 471 + 10
            and 400 - 10 < ry < 410 + 10
            and 228 - 10 <= white_count <= 228 + 50
            and 121 <= grey <= 315
            and dark_purple_count < 15
        ):
            return 43

        if (
            self.frame_height == 720
            and 300 - 10 <= grellow_count <= 300 + 10
            and 375 - 10 < ry < 375 + 10
            and 228 - 10 <= white_count <= 228 + 10
            and 190 <= grey <= 210
            and dark_purple_count < 15
        ):
            return 43

        if (
            self.frame_height == 720
            and 395 - 10 <= grellow_count <= 395 + 10
            and ry < 10
            and 654 - 10 < white_count < 654 + 10
            and 495 <= grey <= 515
            and 140 - 10 < dark_purple_count < 140 + 10
        ):
            return 41

        if (
            self.frame_height == 720
            and 584 - 10 <= grellow_count <= 745
            and ry < 5
            and 430 - 10 < white_count < 440 + 10
            and 960 <= grey <= 994 + 10
            and 127 - 10 < dark_purple_count < 127 + 10
        ):
            return 41

        if (
            self.frame_height == 720
            and 406 - 10 <= grellow_count <= 416
            and ry < 5
            and 1190 < white_count < 1210
            and 418 <= grey <= 438
            and 151 - 10 < dark_purple_count < 151 + 10
        ):
            return 41

        # if (
        # dark_purple_count > 100
        # and teal_count > 100
        # and grellow_count > 100
        # and black_count < 50
        # ):
        # return 39

        if (
            self.frame_height == 720
            and 582 <= grellow_count <= 612
            and 67 <= ry <= 87
            and 270 <= white_count <= 290
            and 120 <= grey <= 140
        ):
            return 44

        if (
            self.frame_height == 1080
            and grellow_count > 220
            and ry > 630
            and white_count < 1100
            and grey < 250
        ):
            return 43

        if grellow_count > 100 and ry > 100 and white_count < 100 and grey < 50:
            return 43

        if purple_count > 8:
            return 42

        for retry in range(0, 9):

            if retry == 8:
                compares = vf_cv.CvHelper.compare_images_histogram(
                    full_roi, self.rank_images[37]
                )

                if compares > 38:
                    return 37

                compares = vf_cv.CvHelper.compare_images_histogram(
                    full_roi, self.rank_images[43]
                )

                if compares > 38:
                    return 43

                compares = vf_cv.CvHelper.compare_images_histogram(
                    full_roi, self.rank_images[44]
                )

                if compares > 38:
                    return 44

                return 0

            ##########################
            ## second roi
            ##########################
            (x, y, w, h) = REGULAR_REGION_ROI
            if retry == 1:
                w = w - 3
                x = x + 2
            elif retry == 2:
                x = x - 29
                y = y - 10
            elif retry == 6 and player_num == 1:
                w = w + 10
            elif retry == 6 and player_num == 2:
                x = x - 5
                w = w + 5
                h = h + 3
            elif retry == 7 and player_num == 2:
                x = x - 2
                w = w + 2
            elif retry == 7 and player_num == 1:
                y = y - 1
                w = w - 1
                x = x + 3
            elif retry == 8 and player_num == 1:
                y = y + 1
                h = h - 3
                x = x + 2

            roi = self.frame[y : y + h, x : x + w]
            all_white_roi = vf_cv.CvHelper.all_but_white_vftv(
                roi, np.array([100, 100, 105])
            )

            imagem = cv2.bitwise_not(all_white_roi)

            text = pytesseract.image_to_string(imagem, timeout=2, config="--psm 7")

            text = re.sub("[^0-9]", "", text)

            if not text.isnumeric() or int(text) < 10:
                continue

            greyCount = vf_cv.CvHelper.count_pixels("#7c7a82", roi)

            rank_int = int(text)
            if rank_int == 38 and white_count == 8:
                return 39

            if rank_int > 46 and retry < 3:
                continue

            if (rank_int >= 40 and greyCount > 130) and rank_int <= 56:
                continue

            if rank_int < 0 or rank_int > 46:
                continue

            if grellow_count > 150 and ry > 60 and rank_int < 30:
                continue

            if gold_count > 300 and rank_int < 36:
                continue

            if (
                grey < 400
                and rank_int > 36
                and white_count > 230
                and grellow_count < 30
            ):
                continue

            if rank_int == 35 and gold_count > 200:
                continue

            if (
                rank_int > 41
                and gold_count > 300
                and teal_count > 10
                and grellow_count > 200
            ):
                continue

            return rank_int
        return 0
