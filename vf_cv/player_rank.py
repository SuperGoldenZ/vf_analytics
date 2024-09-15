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
            (x, y, w, h) = self.REGIONS_480P[region_name]
            x = (int)(x * 1.5)
            y = (int)(y * 1.5)
            w = (int)(w * 1.5) + 25
            h = (int)(h * 1.5)
        elif self.frame_height == 1080:
            (x, y, w, h) = self.REGIONS_480P[region_name]
            x = (int)(x * 2.25)
            y = (int)(y * 2.25)
            w = (int)(w * 2.25)
            h = (int)(h * 2.25)
        return (x, y, w, h)

    # min width 25
    def get_player_rank(self, player_num, debug_player_rank=False):
        FULL_REGION = region_name = f"player{player_num}rank_full"
        FULL_REGION_ROI = self.get_roi(FULL_REGION)

        REGULAR_REGION = f"player{player_num}rank"
        REGULAR_REGION_ROI = self.get_roi(REGULAR_REGION)

        (full_x, full_y, full_w, full_h) = FULL_REGION_ROI

        factor = 1.0

        full_x = int(full_x * factor)
        full_y = int(full_y * factor)
        full_w = int(full_w * factor)
        full_h = int(full_h * factor)

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

        if (
            self.frame_height == 1080
            and 600 <= grellow_count <= 660
            and ry <= 20
            and 1200 <= white_count <= 1340
            and 950 <= grey <= 1280
        ):
            return 41

        if (
            self.frame_height == 1080
            and 178 <= grellow_count <= 198
            and ry <= 5
            and 1860 <= white_count <= 1890
            and 1250 <= grey <= 1280
        ):
            return 40

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
            and 215 <= grellow_count <= 225
            and ry > 700
            and white_count > 1000
            and 178 <= grey <= 198
        ):
            return 43

        if (
            self.frame_height == 720
            and 587 - 10 <= grellow_count <= 587 + 10
            and 390 - 10 < ry < 390 + 10
            and 238 - 10 <= white_count <= 238 + 10
            and 87 - 10 <= grey <= 87 + 10
            and dark_purple_count < 15
        ):
            return 43

        if (
            self.frame_height == 720
            and 574 - 10 <= grellow_count <= 574 + 10
            and 82 - 10 < ry < 82 + 10
            and 360 - 10 <= white_count <= 360 + 10
            and 136 <= grey <= 156
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
            and 471 - 10 <= grellow_count <= 471 + 10
            and 410 - 10 < ry < 410 + 10
            and 228 - 10 <= white_count <= 228 + 10
            and 121 <= grey <= 141
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
