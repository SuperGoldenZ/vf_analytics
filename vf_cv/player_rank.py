import vf_cv.cv_helper
import cv2
import pytesseract
import re
import numpy as np


# 級。 Kyu Group [2 White Characters / No rectangle background]
# 十級 - 一級 10th Kyu to 1st Kyu
#
# 段。 Dan Group [2 White Characters / No rectangle background]
# 初段 - 十段 1st Dan to 10th Dan
#
# 士。 Shi Group [2 White Characters / Wood (light brown) Background]
# 錬士 1 Star - Hunter
# 烈士 2 Star - Raider
# 傑士 3 Star - Barbarian
#
# 者。 Mono Group [2 White Characters / Light Grey Background]
# 強者 1 Star - Defender
# 猛者 2 Star - Sentinel
# 王者 3 Star - Guardian
#
# 人。 Jin Group [2 White Characters / Dark Grey Background]
# 名人 1 Star - Warrior
# 達人 2 Star - Veteran
# 超人 3 Star - Berserker
#
# 将。 Shou Group [2 White Characters / Dark Brown Background]
# 智将 1 Star - Assassin
# 猛将 2 Star - Shatterer
# 闘将 3 Star - Destroyer
#
# 魔王。 Maou Group [3 White Characters / Light Silver Background]
# 大魔王 1 Star - Avenger
# 真魔王 2 Star - Vanquisher
# 天魔王 3 Star - Conqueror
#
# 拳聖。 Kensei Group [3 White Characters / Gold Background]
# 空拳聖 1 Star - Darkslayer
# 撃拳聖 2 Star - Grimslayer
# 剛拳聖 3 Star - Doomslayer
#
# 武帝。 Butei Group [3 White Characters / Dark Silver with Blue + Green in the middle Background
# 獣武帝 1 Star - Tigerclaw
# 鬼武帝 2 Star - Lionheart
# 龍武帝 3 Star - Dragonfang
#
# マスター。 Master Group ("Gods" Ranks)
# 轟雷神 Gouraishin (God of Thunder) - Gold Characters / Blue Background with a white stripe in the middle Stormlord
# 爆焔神 Bakuenshin (God of Flame)- Gold Characters / Orange (top) to Yellow (bottom) Background Magmalord
# 天翔神 Tenshoushin (Soaring Sky God) - Gold Characters / Orange and White (middle) Background Skylord


class PlayerRank:
    REGIONS_480P = {
        "player1rank": (72, 91, 14, 12),
        "player1rank_full": (23, 82, 67, 21),
        "player2rank": (820, 91, 14, 12),
        "player2rank_full": (765, 82, 67, 21),
    }

    REGIONS_720P = {
        "player1rank": (108, 137, 21, 18),
        "player1rank_full_vs": (315, 437, 86, 34 - 16),
        "player2rank_full_vs": (1136, 437, 86, 34 - 16),
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
        "player1rank_small": (383, 452, 17, 12),
        "player2rank_small": (1203, 452, 17, 12),
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

        self.japanese_rank_titles = {}

        self.youtube_video_title = None

    def set_youtube_video_title(self, title):
        self.youtube_video_title = title

    def set_frame(self, frame):
        """Sets the image to extract data from"""
        self.frame = frame
        original_height = self.frame.shape[0]
        if original_height != 720:
            self.frame = cv2.resize(self.frame, (1280, 720))

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
        elif self.frame_height == 1080:
            (x, y, w, h) = self.REGIONS_480P[region_name]
            x = (int)(x * 2.25)
            y = (int)(y * 2.25)
            w = (int)(w * 2.25)
            h = (int)(h * 2.25) - 10
        return (x, y, w, h)

    @staticmethod
    def is_numeric_string(var):
        try:
            float(var)
            return True
        except ValueError:
            return False

    # min width 25
    def get_player_rank(self, player_num, debug_player_rank=False):

        # short circuit with video title
        if (
            self.youtube_video_title is not None
            and (
                "【VFes  VF5us 高段位戦】" in self.youtube_video_title
                or "【VFes高段位戦】" in self.youtube_video_title
                or "名人戦" in self.youtube_video_title
                or "【VFes / VF5us 高段位戦】" in self.youtube_video_title
            )
            and "VS" in self.youtube_video_title
        ):
            split = self.youtube_video_title.strip().split("V")
            index = 0
            if player_num == 2:
                index = len(split) - 1
            else:
                index = len(split) - 2

            if "鬼武帝" in split[index]:
                return 40
            if "龍武帝" in split[index]:
                return 41
            if "轟雷神" in split[index]:
                return 42
            if "爆焔神" in split[index]:
                return 43
            if "天翔神" in split[index]:
                return 44
            if "幻冥神" in split[index]:
                return 45
            if "超煌神" in split[index]:
                return 46

        FULL_REGION = f"player{player_num}rank_full"
        FULL_REGION_ROI = self.get_roi(FULL_REGION)

        REGULAR_REGION = f"player{player_num}rank"
        REGULAR_REGION_ROI = self.get_roi(REGULAR_REGION)

        (full_x, full_y, full_w, full_h) = FULL_REGION_ROI

        full_roi = self.frame[full_y : full_y + full_h, full_x : full_x + full_w]

        white_count = vf_cv.CvHelper.count_pixels("#000000", full_roi, 50)
        purple_count = vf_cv.CvHelper.count_pixels("#7600b9", full_roi)
        grey = vf_cv.CvHelper.count_pixels("#908f95", full_roi)
        dark_purple_count = vf_cv.CvHelper.count_pixels("#3a165e", full_roi, 15)
        teal_count = vf_cv.CvHelper.count_pixels("#558784", full_roi)
        grellow_count = vf_cv.CvHelper.count_pixels("#8e9a52", full_roi)
        gold_count = vf_cv.CvHelper.count_pixels("#e2cb87", full_roi)
        ry = vf_cv.CvHelper.count_pixels("#cc5b31", full_roi)
        black_count = vf_cv.CvHelper.count_pixels("#000000", full_roi, 5)
        yg = vf_cv.CvHelper.count_pixels("#6a8b8e", full_roi, 10)
        green_gold = vf_cv.CvHelper.count_pixels("#8b752b", full_roi, 10)
        orange = vf_cv.CvHelper.count_pixels("#c26e30", full_roi, 15)
        mint = vf_cv.CvHelper.count_pixels("#8bcc98", full_roi, 10)

        # full_roi_bw = self.frame[full_y-10 : full_y + full_h+10, full_x-10 : full_x + full_w+10]
        # full_roi_bw = cv2.cvtColor(full_roi_bw, cv2.COLOR_BGR2GRAY)

        debug_string = f"{self.frame_height}_mint{mint}_gg{green_gold}_{orange}_gre{grellow_count}_ry{ry}_wc{white_count}_g{grey}_dp{dark_purple_count}_yg{yg}"

        if debug_player_rank:
            cv2.imshow(
                debug_string,
                full_roi,
            )

            # print(debug_string)
            # cv2.imshow("bw", full_roi_bw)
            cv2.waitKey()

        ##########################
        ## second roi
        ##########################
        (x, y, w, h) = self.get_roi(f"player{player_num}rank_full_vs")

        frame_copy = self.frame.copy()

        roi = frame_copy[y : y + h, x : x + w]
        all_white_roi = vf_cv.CvHelper.all_but_white_vftv(
            roi, np.array([195, 185, 185])
        )

        imagem = cv2.bitwise_not(all_white_roi)

        text = pytesseract.image_to_string(imagem, timeout=2, config="--psm 7")
        text = text.replace("sth", "5th")
        text = text.replace("Sth", "5th")
        text = text.replace("Ist", "1st")
        text = text.replace("Tst", "1st")
        text = text.replace("tst", "1st")
        text = text.replace("6ti", "6th")
        text = text.replace("Ath", "4th")

        kyu_pattern = r"(\d{1,2})th"
        if "rd" in text:
            kyu_pattern = r"(\d{1,2})rd"
        if "st" in text:
            kyu_pattern = r"(\d{1,2})st"
        if "nd" in text:
            kyu_pattern = r"(\d{1,2})nd"

        matches = re.findall(kyu_pattern, text)

        is_dan = False

        # todo update here
        if debug_player_rank:
            print(f"{x} {y} {w} {h} {text}")
            print("kyu matches")
            print(matches)
            cv2.imshow(f"player rank full {self.frame_height}", self.frame)
            cv2.imshow(f"rank [{text}]", imagem)
            cv2.imshow(f"roi [{text}]", roi)
            cv2.waitKey()

        if "st dan" in text:
            return 11

        if "Darh" in text:
            return 23

        if "Wart" in text:
            return 27

        if "Raider" in text:
            return 22

        if "arrior" in text:
            return 27

        if "Hunter" in text:
            return 21

        if "i" in text and "23" in text:
            return 23

        is_kyu = "k" in text
        if (
            is_kyu
            and len(matches) > 0
            and PlayerRank.is_numeric_string(matches[0])
            # and (matches[0]) != "5"  #skip for 5th 9th
        ):
            if debug_player_rank:
                print(
                    f"returning kyu {(int(matches[0]))}  returning {11-int(matches[0])}"
                )
            return 11 - int(matches[0])

        is_dan = "d" in text
        fifth = len(matches) > 0 and matches[0] == "5"

        if (
            is_dan
            and len(matches) > 0
            and PlayerRank.is_numeric_string(matches[0])
            and (matches[0]) != "5"  # skip for 5th 9th
        ):
            if debug_player_rank:
                print(
                    f"returning dan {(int(matches[0]))}  returning {10+int(matches[0])}"
                )
            return 10 + int(matches[0])

        text = re.sub("[^0-9]", "", text)

        # retry with small
        if not text.isnumeric() or (matches[0]) == "5":  # skip for 5th 9th:
            (x, y, w, h) = self.get_roi(f"player{player_num}rank_small")

            if debug_player_rank:
                print(f"retru rpo {x} {y} {w} {h}")
            frame_copy = self.frame.copy()
            roi = frame_copy[y : y + h, x : x + w]

            all_white_roi = vf_cv.CvHelper.all_but_white_vftv(
                roi, np.array([165, 160, 160])
            )

            all_white_roi = cv2.cvtColor(all_white_roi, cv2.COLOR_BGR2GRAY)

            imagem = cv2.bitwise_not(all_white_roi)
            imagem = vf_cv.CvHelper.add_white_column(imagem, 5, True)
            imagem = vf_cv.CvHelper.add_white_row(imagem, 5)

            # gray_image_t = vf_cv.CvHelper.add_white_row(gray_image_t, 15)

            text = pytesseract.image_to_string(
                imagem,
                timeout=2,
                config="--psm 7 -c tessedit_char_whitelist=0123456789",
            )
            text = text.strip()

            if debug_player_rank:
                print(f"retry! {text}")
                print(f"{x} {y} {w} {h} {text}")
                print("kyu matches")
                print(matches)
                cv2.imshow(f"player rank full {self.frame_height}", self.frame)
                cv2.imshow(f"rank [{text}]", imagem)
                cv2.imshow(f"roi [{text}]", roi)
                cv2.waitKey()
                cv2.waitKey()

            if fifth and is_dan and text == "14":
                return 19

            if not text.isnumeric():
                raise UnrecognizePlayerRankException(debug_string)

        rank_int = int(text)
        if rank_int <= 0 or rank_int >= 46:
            raise UnrecognizePlayerRankException(debug_string)

        return rank_int


class UnrecognizePlayerRankException(Exception):
    pass
