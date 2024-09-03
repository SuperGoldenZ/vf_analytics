import cv2
import numpy as np
import re
import pytesseract
import vf_cv.cv_helper


class Character:
    frame = None
    frame_height = None

    REGIONS_480P = {
        "player1character": (35, 228, 245, 32),
        "player2character": (584, 228, 245, 32),
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

    @profile
    def get_character_name(self, player_num):
        """Returns the name of the character a certain player is using"""
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

            threshold_value = 250
            _, thresholded_image = cv2.threshold(
                gray_image, threshold_value, 255, cv2.THRESH_BINARY
            )

            n_white_pix = np.sum(thresholded_image == 255)
            # print(n_white_pix)

            # cv2.imshow("roi", roi)
            # cv2.imshow("frame", gray_image)
            # cv2.waitKey()

            if self.frame_height == 720:
                if n_white_pix == 1946:
                    return "Shun Di"
                if n_white_pix == 2944 or n_white_pix == 2430 or n_white_pix == 2036:
                    return "Jean"
                if n_white_pix == 3664:
                    return "Lion"
                if n_white_pix == 3833:
                    return "Aoi"
                if n_white_pix == 2778:
                    return "Brad"

            if False:
                if height == 720 and 3814 - 10 <= n_white_pix <= 3814 + 10:
                    print("short circuit kage")
                    return "Kage"

                if height == 720 and 3384 - 10 <= n_white_pix <= 3814 + 10:
                    print("short circuit Jean")
                    return "Jean"

                if 1400 <= n_white_pix <= 1500:

                    print("short circuit kage")
                    return "Kage Maru"

                if 1200 <= n_white_pix <= 1300:
                    print("short circuit Jean")
                    return "Jean"
                if retry == 1 and player_num == 1:
                    w = w - 75
                    h = h - 15
                elif retry == 1 and player_num == 2:
                    x = x - 20
                    w = w + 20

                if retry == 2 and player_num == 1:
                    x = x + 20
                    w = w - 100
                    h = h - 20
                elif retry == 2 and player_num == 2:
                    x = x + 50
                    w = w - 100

                if retry == 3 and player_num == 1:
                    x = x + 20
                    w = w - 100
                    h = h - 20
                elif retry == 3 and player_num == 2:
                    x = x + 175
                    w = w - 175
                    y = y + 10
                    h = h - 10

            roi = self.frame[y : y + h, x : x + w]

            white_only_roi = vf_cv.CvHelper.all_but_white(roi)
            text = pytesseract.image_to_string(white_only_roi, config="--psm 7").strip()
            # print(f"{text}")
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
