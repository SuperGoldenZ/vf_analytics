import cv2
import numpy as np
import pytesseract
import vf_cv.cv_helper
from datetime import datetime


class VsScreen:
    frame = None
    frame_height = None

    REGIONS_480P = {
        "date": (35, 228, 245, 32),
        "player2character": (584, 228, 245, 32),
    }

    REGIONS_1080P = {
        "date": (694-20, 60-20, 532+20, 73+20),        
        "player1_ringname": (98-5, 708-3, 442+5, 35),
        "player2_ringname": (1322-5, 708-3, 442+5, 35),
    }

    def set_frame(self, frame):
        """Sets the image to extract data from"""
        self.frame = frame
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
            (x, y, w, h) = self.REGIONS_1080P[region_name]
        elif self.frame_height == 1080:
            #print(f"getting 1080p {region_name}")
            (x, y, w, h) = self.REGIONS_1080P[region_name]
        return (x, y, w, h)

    @staticmethod
    def fix_slashes(s):
        # Convert the string to a list to allow modifications
        s_list = list(s)
        
        # Check and replace the fifth character (index 4) if it's '1'
        if len(s_list) > 4 and s_list[4] == '1':
            s_list[4] = '/'
        
        # Check and replace the eighth character (index 7) if it's '1'
        if len(s_list) > 7 and s_list[7] == '1':
            s_list[7] = '/'
                
        # Join the list back into a string
        return ''.join(s_list)

    def get_date(self, debug=True):
        #print(f"getting date {self.frame_height}")
        (x, y, w, h) = self.get_roi("date")
        if (self.frame_height == 720):
            x = (int) (x / 1.5)
            y = (int) (y / 1.5)
            w = (int) (w / 1.5)
            h = (int) (h / 1.5)

        date_roi = self.frame[y : y + h, x : x + w]
        date_roi_white = vf_cv.cv_helper.CvHelper.all_but_white_vftv(date_roi, np.array([200, 200, 200]))

        grayscale_image = cv2.cvtColor(date_roi_white, cv2.COLOR_BGR2GRAY)
        inverted_image = cv2.bitwise_not(grayscale_image)

        text = pytesseract.image_to_string(inverted_image, config="--psm 13 -c tessedit_char_whitelist=0123456789/").strip()
        text = self.fix_slashes(text)
        
        if debug:
            cv2.imshow("vs_screen debug", inverted_image)
            print(f"date {text}")
            cv2.waitKey()
        
        if self.is_valid_date_format(text):            
            return text
        
        #print(self.fix_and_validate_date(text))
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
        if (self.frame_height == 360):
            return None
        
        (x, y, w, h) = self.get_roi(f"player{playernum}_ringname")
        if (self.frame_height == 720):
            x = (int) (x / 1.5)
            y = (int) (y / 1.5)
            w = (int) (w / 1.5)
            h = (int) (h / 1.5)

        ringname_roi = self.frame[y : y + h, x : x + w]
        ringname_roi_white = vf_cv.cv_helper.CvHelper.all_but_white_vftv(ringname_roi)

        grayscale_image = cv2.cvtColor(ringname_roi_white, cv2.COLOR_BGR2GRAY)
        inverted_image = cv2.bitwise_not(grayscale_image)
        
        text = pytesseract.image_to_string(inverted_image, config="--psm 7 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_").strip()
        
        if debug_ringname:
            cv2.imshow("ringname_roi_white", inverted_image)            
            print(text)
            cv2.waitKey()
        
        return (text)        
