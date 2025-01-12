import cv2
import numpy as np
import re
import pytesseract
import vf_cv.cv_helper


class Character:
    frame = None
    frame_height = None

    REGIONS_480P = {
        "player1character": (35, 228, 150, 32),
        "player2character": (584, 228, 245, 32),
    }

    def __init__(self):
        self.youtube_video_title = None

    def set_frame(self, frame):
        """Sets the image to extract data from"""
        self.frame = frame
        self.frame_height = frame.shape[0]

    def set_youtube_video_title(self, youtube_video_title):
        self.youtube_video_title = youtube_video_title

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

    def get_character_name(self, player_num, debug_character=False):
        """Returns the name of the character a certain player is using"""

        parse_title = (
            self.youtube_video_title is not None
            and (
                "【VFes高段位戦】" in self.youtube_video_title
                or "【VFes  VF5us 高段位戦】" in self.youtube_video_title
                or "名人戦" in self.youtube_video_title
                or "【VFes / VF5us 高段位戦】" in self.youtube_video_title
            )
            and "VS" in self.youtube_video_title
        )

        if parse_title:
            split = self.youtube_video_title.strip().split("V")
            # rm print(split)
            offset = len(split) - 3

            if "影丸" in split[player_num + offset]:
                return "Kage"
            if "パイ" in split[player_num + offset]:
                return "Pai"
            if "鷹嵐" in split[player_num + offset]:
                return "Taka"
            if "梅小路葵" in split[player_num + offset]:
                return "Aoi"
            if "ブラッド" in split[player_num + offset]:
                return "Brad"
            if "ウルフ" in split[player_num + offset]:
                return "Wolf"
            if "ベネッサ" in split[player_num + offset]:
                return "Vanessa"
            if "ジャッキー" in split[player_num + offset]:
                return "Jacky"
            if "ラウ" in split[player_num + offset]:
                return "Lau"
            if "結城晶" in split[player_num + offset]:
                return "Akira"
            if "リオン" in split[player_num + offset]:
                return "Lion"
            if "ジャン" in split[player_num + offset]:
                return "Jean"
            if "日守剛" in split[player_num + offset]:
                return "Goh"
            if "ジェフリー" in split[player_num + offset]:
                return "Jeffry"
            # 14
            if "雷飛" in split[player_num + offset]:
                return "Lei Fei"

            if "舜帝" in split[player_num + offset]:
                return "Shun"

            if "サラ" in split[player_num + offset]:
                return "Sarah"

            if "エル・ブレイズ" in split[player_num + offset]:
                return "Blaze"

            if "アイリーン" in split[player_num + offset]:
                return "Eileen"

        region_name = f"player{player_num}character"
        for retry in range(1, 3):
            (x, y, w, h) = self.get_roi(region_name)

            xFactor = 0
            if player_num == 1:
                xFactor = 20

            x = int(x) - xFactor
            y = int(y)
            w = int(w)
            h = int(h)

            roi = self.frame[y : y + h, x : x + w]

            gray_image = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            threshold_value = 240
            _, thresholded_image = cv2.threshold(
                gray_image, threshold_value, 255, cv2.THRESH_BINARY
            )

            thresholded_image = cv2.bitwise_not(thresholded_image)

            first_letter = vf_cv.CvHelper.trim(thresholded_image)

            (height, width) = thresholded_image.shape

            n_white_pix = np.sum(thresholded_image == 255)
            n_white_pix_first = np.sum(first_letter == 255)

            if debug_character is True:
                cv2.imshow(
                    f"p{player_num} char {self.frame_height} {n_white_pix_first} letter {first_letter.shape[1]} x {first_letter.shape[0]}",
                    first_letter,
                )

                cv2.imshow(
                    f"p{player_num} char {self.frame_height} {n_white_pix} {width} {height} roi",
                    roi,
                )

                cv2.imshow(
                    f"p{player_num} threshold char {self.frame_height} {n_white_pix} {width} {height}",
                    thresholded_image,
                )

                cv2.waitKey()

            if self.frame_height == 360:
                # b, g, r = roi[0, 0]
                # if player_num == 2 and r == 235 and g == 190 and b == 48:
                # return "Lei Fei"

                similarity = vf_cv.CvHelper.color_similarity(roi[0, 0], (32, 144, 194))
                if player_num == 1 and similarity >= 0.95:
                    # print(f"p{player_num} lei fei with {similarity}")
                    return "Lei Fei"

                b, g, r = roi[5, 45]
                if player_num == 2 and b > 230 and r > 230 and g > 230:
                    return "Akira"

                red = 127
                green = 89
                blue = 23
                similarity = vf_cv.CvHelper.color_similarity(
                    roi[0, 0], (blue, green, red)
                )
                if player_num == 2 and similarity >= 0.95:
                    # print(f"p{player_num} lei fei with {similarity}")
                    return "Lei Fei"

                red = 67
                green = 91
                blue = 188
                if (
                    player_num == 1
                    and vf_cv.CvHelper.color_similarity(
                        roi[10, 165], (green, blue, red)
                    )
                    >= 0.66
                ):
                    return "Kage"

                red = 240
                green = 185
                blue = 154

                if (
                    player_num == 2
                    and vf_cv.CvHelper.color_similarity(roi[0, 0], (blue, green, red))
                    > 0.95
                ):
                    return "Blaze"

            if self.frame_height == 720 and 592 - 10 <= n_white_pix_first <= 592 + 10:
                return "Lion"

            if (
                self.frame_height == 720
                and 484 - 10 <= n_white_pix_first <= 484 + 10
                and first_letter.shape[0] < 30
            ):
                return "Vanessa"

            if (
                self.frame_height == 720
                and 484 - 10 <= n_white_pix_first <= 484 + 10
                and 492 - 10 <= first_letter.shape[0] < 492 + 10
            ):
                return "Lion"

            if self.frame_height == 720 and 309 - 10 <= n_white_pix_first <= 309 + 10:
                return "Jean"

            if (
                self.frame_height == 720
                and 429 - 5 <= n_white_pix_first <= 429 + 5
                and first_letter[2, 7] == 0
            ):
                return "Akira"

            if self.frame_height == 720 and 641 - 10 <= n_white_pix_first <= 641 + 10:
                return "Kage"

            if self.frame_height == 720:
                if n_white_pix == 1946:
                    return "Shun Di"
                if n_white_pix == 2944 or n_white_pix == 2430 or n_white_pix == 2036:
                    return "Jean"
                if n_white_pix == 3664:
                    return "Lion"
                if n_white_pix == 3833:
                    return "Aoi"
                if n_white_pix == 2778 or n_white_pix == 2761:
                    return "Brad"
                if 2738 - 10 <= n_white_pix <= 2738 + 10:
                    return "Taka"

            roi = self.frame[y : y + h, x : x + w]

            text = pytesseract.image_to_string(
                thresholded_image,
                config="--psm 7 -c tessedit_char_whitelist=ABCDEFGIJKLMNOPQRSTUVWXYZ\ abcdefghijklmnopqrstuvwxyz",
            ).strip()

            if debug_character:
                print(f"got text [{text}]")
            if "Ejleen" in text:
                return "Eileen"
            if "Tagan Kirin" in text:
                return "Jean"
            if "Brad" in text:
                text = "Brad"
            if "Kage" in text:
                text = "Kage"
            if "Akira" in text:
                text = "Akira"
            if "Blaze" in text:
                text = "Blaze"
            if "Wolf" in text:
                text = "Wolf"
            if "Fei" in text:
                return "Lei Fei"
            if "Lei" in text:
                return "Lei Fei"
            if "Aoi" in text:
                return "Aoi"
            if "Akira" in text:
                return "Akira"
            if "Jean" in text:
                return "Jean"
            if "Lau" in text:
                return "Lau"
            if "Taka" in text:
                return "Taka"
            if "Sarah" in text:
                return "Sarah"
            if "Jacky" in text:
                return "Jacky"
            if "Shun" in text:
                return "Shun"
            if "Goh" in text:
                return "Goh"
            if "Lion" in text:
                return "Lion"
            if "Vanessa" in text:
                return "Vanessa"
            if "Jeffry" in text:
                return "Jeffry"
            if "Pai" in text:
                return "Pai"
            if "Goh" in text:
                return "Goh"
            if "Eileen" in text:
                return "Eileen"

            if text == "EI Blaze":
                text = "Blaze"

            pattern = r"^[a-zA-Z]{4} [a-zA-Z]{4}$"

            if re.match(pattern, text):
                return "Kage"

            if self.is_vf_character_name(text):
                return str.replace(text, "\n\x0c", "")

            print(f"\t\t\t\tDid not match character name {text}")
        return None

    @staticmethod
    def is_vf_character_name(name):
        if "Lau" in name:
            return True
        if "Lion" in name:
            return True
        if "Wolf" in name:
            return True
        if "Pai" in name:
            return True
        if "Jeff" in name:
            return True
        if "Aoi" in name:
            return True
        if "Vanessa" in name:
            return True
        if "Blaze" in name:
            return True
        if "Akira" in name:
            return True
        if "Kage" in name:
            return True
        if "Eileen" in name:
            return True
        if "Lau" in name:
            return True
        if "Take" in name:
            return True
        if "Shun" in name:
            return True
        if "Jacky" in name:
            return True
        if "Sarah" in name:
            return True
        if "Goh" in name:
            return True
        if "Lei Fei" in name:
            return True
        if "Brad" in name:
            return True
        return False
