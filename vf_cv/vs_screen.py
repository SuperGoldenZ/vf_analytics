"""Extracts information from the VS screen"""
from datetime import datetime
import cv2
import numpy as np
import pytesseract
import vf_cv.cv_helper

class VsScreen:
    """Extracts information from the VS screen"""
    frame = None
    frame_height = None

    REGIONS_480P = {
        "date": (35, 228, 245, 32),
        "player2character": (584, 228, 245, 32),
        "stage": (342, 295, 200, 25),
    }

    REGIONS_720P = {
        "stage": (553, 442, 200, 25),
        "date": (450, 27, 368, 62),
        "player1_ringname": (60, 470, 298, 23),
        "player2_ringname": (878, 470, 298, 23),
    }

    REGIONS_1080P = {
        "date": (694 - 20, 60 - 20, 532 + 20, 73 + 20),
        "player1_ringname": (98 - 5, 708 - 3, 442 + 5, 35),
        "player2_ringname": (1322 - 5, 708 - 3, 442 + 5, 35),
        "stage": (793, 660, 350, 50),
    }

    IS_VS_RED_COORDINATES = {
        360: [int(91 * 0.75), int(21 * 0.75)],
        480: [91, 21],
        720: [int(91 * 1.5), int(21 * 1.5)],
        1080: [int(91 * 2.25), int(21 * 2.25)],
    }

    IS_VS_BLUE_COORDINATES = {
        360: [int(91 * 0.75), int(847 * 0.75)],
        480: [91, 847],
        720: [int(91 * 1.5), int(847 * 1.5)],
        1080: [int(91 * 2.25), int(847 * 2.25)],
    }

    IS_P2_BLUE_COORDINATES = {
        360: [int(296 * 0.75), int(587 * 0.75)],
        480: [296, 587],
        720: [int(296 * 1.5), int(587 * 1.5)],
        1080: [int(296 * 2.25), int(587 * 2.25)],
    }

    VS_GRAY_COORDINATES = {
        360: [int(186 * 0.75), int(369 * 0.75)],
        480: [186, 369],
        720: [int(186 * 1.5), int(369 * 1.5)],
        1080: [int(186 * 2.25), int(369 * 2.25)],
    }

    VS_BLACK_COORDINATES = {
        360: [155, 275],
        480: [178, 363],
        720: [int(178 * 1.5), int(363 * 1.5)],
        1080: [int(178 * 2.25), int(363 * 2.25)],
    }

    def set_frame(self, frame):
        """Sets the image to extract data from"""
        self.frame = frame.copy()
        self.frame_height = frame.shape[0]

    @staticmethod
    def is_valid_date_format(date_string):
        try:
            datetime.strptime(date_string, "%Y/%m/%d")
            return True
        except ValueError:
            return False

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
            # print(f"getting 1080p {region_name}")
            (x, y, w, h) = self.REGIONS_1080P[region_name]
        return (x, y, w, h)

    @staticmethod
    def fix_slashes(s):
        # Convert the string to a list to allow modifications
        s_list = list(s)

        # Check and replace the fifth character (index 4) if it's '1'
        if len(s_list) > 4 and s_list[4] == "1":
            s_list[4] = "/"

        # Check and replace the eighth character (index 7) if it's '1'
        if len(s_list) > 7 and s_list[7] == "1":
            s_list[7] = "/"

        # Join the list back into a string
        return "".join(s_list)

    @staticmethod
    def fix_slashes_western_format(s):
        # Convert the string to a list to allow modifications
        s_list = list(s)

        # Check and replace the fifth character (index 4) if it's '1'
        if len(s_list) > 2 and s_list[2] == "1":
            s_list[2] = "/"

        # Check and replace the eighth character (index 7) if it's '1'
        if len(s_list) > 5 and s_list[5] == "1":
            s_list[5] = "/"

        # Join the list back into a string
        return "".join(s_list)

    def get_date(self, debug=True):
        # print(f"getting date {self.frame_height}")
        (x, y, w, h) = self.get_roi("date")

        date_roi = self.frame[y : y + h, x : x + w]
        date_roi_white = vf_cv.cv_helper.CvHelper.all_but_white_vftv(
            date_roi, np.array([200, 200, 200])
        )

        grayscale_image = cv2.cvtColor(date_roi_white, cv2.COLOR_BGR2GRAY)
        inverted_image = cv2.bitwise_not(grayscale_image)

        text = pytesseract.image_to_string(
            inverted_image, config="--psm 13 -c tessedit_char_whitelist=0123456789/"
        ).strip()
        fixed_text = self.fix_slashes(text)
        if not self.is_valid_date_format(fixed_text):
            fixed_text = self.fix_slashes_western_format(text)

            try:
                fixed_text = datetime.strptime(fixed_text, "%m/%d/%Y").strftime(
                    "%Y/%m/%d"
                )
            except:
                return ""

        if debug:
            cv2.imshow("vs_screen debug", inverted_image)
            print(f"date {text} {fixed_text}")
            cv2.waitKey()

        if self.is_valid_date_format(fixed_text):
            return fixed_text

        # print(self.fix_and_validate_date(text))
        return self.fix_and_validate_date(text)

    @staticmethod
    def fix_and_validate_date(date_string):
        try:
            # Extract and adjust the string to "YYYY/MM/DD"
            year, rest = date_string.split("/")
            month = rest[:2]
            day = rest[2:-1]  # Remove the last character

            # Reconstruct the corrected date string
            corrected_date = f"{year}/{month}/{day}"

            # Validate the corrected date format
            datetime.strptime(corrected_date, "%Y/%m/%d")
            return corrected_date
        except (ValueError, IndexError):
            return None

    def get_ringname(self, playernum, debug_ringname=False):
        if self.frame_height == 360:
            return None

        (x, y, w, h) = self.get_roi(f"player{playernum}_ringname")

        ringname_roi = self.frame[y : y + h, x : x + w]
        ringname_roi_white = vf_cv.cv_helper.CvHelper.all_but_white_vftv(ringname_roi)

        grayscale_image = cv2.cvtColor(ringname_roi_white, cv2.COLOR_BGR2GRAY)
        inverted_image = cv2.bitwise_not(grayscale_image)

        ringname = pytesseract.image_to_string(
            inverted_image,
            # config="--psm 7 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_",
            config="--psm 7 -l jpn+eng+kor",
        ).strip()

        if debug_ringname:
            cv2.imshow(
                f"ringname_roi_white {self.frame_height} {ringname}", inverted_image
            )
            print(ringname)
            cv2.waitKey()

        ringname = ringname.replace(",", "")
        ringname = ringname.replace('"', "")
        return ringname

    def is_vs_ver1(self, debug=False):
        frame = self.frame
        height = frame.shape[0]  # Get the dimensions of the frame

        result = True

        debug_message = "is_vs roi"
        r1 = frame[
            self.IS_VS_RED_COORDINATES[height][0], self.IS_VS_RED_COORDINATES[height][1]
        ][2]
        r2 = frame[
            self.IS_VS_RED_COORDINATES[height][0] + 25,
            self.IS_VS_RED_COORDINATES[height][1] + 75,
        ][2]

        if r1 < 80 and r2 < 80:
            debug_message = f"{debug_message} false 1"
            result = False
        else:
            (y1, x1) = self.IS_VS_BLUE_COORDINATES[height]
            b1 = frame[y1, x1][0]

            b2 = frame[y1 + 25, x1 - 125][0]
            if height == 360:
                b2 = frame[y1 + 25, 600][0]

            if (b1 < 80) and (b2 < 80):
                debug_message = f"{debug_message} false 2  b1[{b1}] b2[{b2}] y{y1} x{x1}  {b1 < 80}  {b2 < 80}"
                result = False
            else:
                (b, g, r) = frame[
                    self.IS_P2_BLUE_COORDINATES[height][0],
                    self.IS_P2_BLUE_COORDINATES[height][1],
                ]
                if b < 80:
                    debug_message = f"{debug_message} false 3"
                    result = False
                else:
                    (b, g, r) = frame[
                        self.VS_GRAY_COORDINATES[height][0],
                        self.VS_GRAY_COORDINATES[height][1],
                    ]
                    if b < 90 or g < 90 or r < 90:
                        debug_message = f"{debug_message} false 4"
                        result = False
                    else:
                        (y, x) = self.VS_BLACK_COORDINATES[height]
                        (b, g, r) = frame[y, x]
                        if b > 40 or g > 40 or r > 40:
                            debug_message = (
                                f"{debug_message} false 5 for {y} {x}  {r}_{g}_{b}"
                            )
                            result = False

        if debug:
            cv2.imshow(debug_message, frame)
            cv2.waitKey()

        return result

    @staticmethod
    def all_but_grey(roi):
        lower_white = np.array([165, 165, 165])  # Lower bound of white color
        upper_white = np.array([255, 255, 255])  # Upper bound of white color
        mask = cv2.inRange(roi, lower_white, upper_white)

        # Apply the mask to keep only white areas in the ROI
        white_only_roi = cv2.bitwise_and(roi, roi, mask=mask)
        return white_only_roi

    def get_stage(self, debug_stage=False):
        region_name = "stage"
        frame = self.frame

        height = frame.shape[0]  # Get the dimensions of the frame
        (x, y, w, h) = self.get_roi(region_name)

        roi = frame[y : y + h, x : x + w]

        all_white_roi = VsScreen.all_but_grey(roi)

        imagem = cv2.bitwise_not(all_white_roi)

        text = pytesseract.image_to_string(imagem, config="--psm 6")
        text = str.replace(text, "\n\x0c", "").upper()

        if debug_stage:
            cv2.imshow(f"{height} stage [{text}]", frame)
            cv2.imshow(f"{height} {text}", imagem)
            cv2.imshow(f"{height} original roi", roi)
            cv2.waitKey()

        if text == "WATER FALLS":
            return "Waterfalls"

        if text == "ISLAND":
            return "Island"

        if text == "SSFAND":
            return "Island"

        if text == "TAMPIA":
            return "Temple"

        if len(text) == 6 and "LAND" in text:
            return "Island"

        if "ARENA" == text:
            return "Arena"

        if "PALCE" == text:
            return "Palace"

        if "AURORA" == text:
            return "Aurora"

        if "TEMPLE" == text:
            return "Temple"

        if "SUMO RING" == text:
            return "Sumo Ring"

        if "RUINS" == text:
            return "Ruins"

        if "STATUES" in text or "STAT" in text:
            return "Statues"

        if "GREAT WALL" == text:
            return "Great Wall"

        if "WALL" in text:
            return "Great Wall"

        if "CITY" in text:
            return "City"

        if "TERRACE" == text:
            return "Terrace"

        if "RIVER" == text:
            return "River"

        if "FALL" in text:
            return "Waterfalls"

        if "WATER" in text:
            return "Waterfalls"

        if "WATERFALLS" in text:
            return "Waterfalls"

        if "GRASS" in text:
            return "Grassland"

        if "DEEP" in text:
            return "Deep Mountain"

        if "BROKEN" in text or "House" in text:
            return "Broken House"

        if "GENESIS" == text:
            return "Genesis"

        if "SHRINE" == text:
            return "Shrine"

        if text == "TRAINING ROOM":
            return "Training Room"

        if "SNOW" in text:
            return "Snow Mountain"

        if "PALACE" in text:
            return "Palace"

        if "TEMPLE" in text:
            return "Temple"

        if "RUINS" in text:
            return "Ruins"

        return None
