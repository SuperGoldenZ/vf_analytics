"""This module gives information about a frame that shows a round being won"""

import cv2
import vf_cv.cv_helper

class WinningFrame:
    frame = None
    frame_height = None

    REGIONS_480P = {
         'player1_rounds': (307, 50, 55, 15)
        ,'player2_rounds': (475, 50, 80, 15)
        ,'player1_health': (111, 33, 265, 8)
        ,'player2_health': (483, 36, 265, 8)
        ,'stage': (342, 295, 200, 25)
        ,'player1ringname':  (43, 315, 209, 18)
        ,'player2ringname':  (589, 315, 209, 18)
        ,'player1character': (35,   228,   245, 32)
        ,'player2character': (584,  228,   245, 32)
        ,'all_rounds': (247, 45, 404, 31)
        ,'vs': (343, 173, 172, 85)
        ,'ko': (250, 170, 350, 140)
        ,'excellent': (75, 200, 700, 80)
        ,'ro': (185, 204, 484, 80)
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
    
    def is_ringout(self, debug=False):
        region_name = "ro"
        (x, y, w, h) = self.get_roi(region_name)

        roi = self.frame[y : y + h, x : x + w]

        green_count = vf_cv.CvHelper.count_pixels("#07a319", roi, override_tolerance=15)
        light_green = vf_cv.CvHelper.count_pixels("#91ff92", roi, override_tolerance=15)
        red_tekken_count = vf_cv.CvHelper.count_pixels("#e42e20", roi, override_tolerance=15)

        if (debug):
            cv2.imshow("roi", roi)
            print(f"green {green_count}  red {red_tekken_count}  light_green {light_green}")
            print(green_count > 300 or red_tekken_count > 2000)
            cv2.waitKey()
        return green_count + light_green > 300 or red_tekken_count > 2000