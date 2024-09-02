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
            w = (int)(w * 1.5)
            h = (int)(h * 1.5)
        return (x, y, w, h)

    # min width 25
    def get_player_rank(self, player_num):
        FULL_REGION = region_name = f"player{player_num}rank_full"
        FULL_REGION_ROI = self.get_roi(FULL_REGION)

        REGULAR_REGION = f"player{player_num}rank"
        REGULAR_REGION_ROI = self.get_roi(REGULAR_REGION)

        for retry in range(0, 9):

            (x, y, w, h) = FULL_REGION_ROI

            factor = 1.0

            if self.frame_height == 720:
                factor = 1.5

            x = int(x * factor)
            y = int(y * factor)
            w = int(w * factor)
            h = int(h * factor)

            roi = self.frame[y : y + h, x : x + w]

            white_count = vf_cv.CvHelper.count_pixels("#000000", roi, 50)
            purple_count = vf_cv.CvHelper.count_pixels("#7600b9", roi)
            grey = vf_cv.CvHelper.count_pixels("#908f95", roi)
            dark_purple_count = vf_cv.CvHelper.count_pixels("#3a165e", roi)
            teal_count = vf_cv.CvHelper.count_pixels("#558784", roi)
            grellow_count = vf_cv.CvHelper.count_pixels("#8e9a52", roi)
            gold_count = vf_cv.CvHelper.count_pixels("#e2cb87", roi)
            ry = vf_cv.CvHelper.count_pixels("#cc5b31", roi)
            black_count = vf_cv.CvHelper.count_pixels("#000000", roi, 5)

            if (
                dark_purple_count > 100
                and teal_count > 100
                and grellow_count > 100
                and black_count < 50
            ):
                return 39

            if grellow_count > 100 and ry > 100 and white_count < 100 and grey < 50:
                return 43

            if purple_count > 8:
                return 42

            if retry == 8:
                compares = vf_cv.CvHelper.compare_images_histogram(
                    roi, self.rank_images[37]
                )

                if compares > 38:
                    return 37

                compares = vf_cv.CvHelper.compare_images_histogram(
                    roi, self.rank_images[43]
                )

                if compares > 38:
                    return 43

                compares = vf_cv.CvHelper.compare_images_histogram(
                    roi, self.rank_images[44]
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
