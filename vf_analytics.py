import re
import logging
import cv2
import numpy as np
import vf_cv
import pytesseract

# PS4 Resolution is 1920 x 1080 1080P

logger = logging.getLogger(__name__)
#logging.basicConfig(
    #filename="vf_analytics.log",
    #encoding="utf-8",
    #level=logging.ERROR,
    #format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
#)

resolution = "1080p"
excellent = cv2.imread("assets/test_images/480p/excellent/excellent.png")

# alexRegions
regions_default = {
    "player1rank": (125, 156, 22, 18),
    "player2rank": (1410, 158, 22, 18),
    "player1_rounds": (519, 78, 106, 36),
    "player2_rounds": (840, 78, 106, 36),
    "stage": (619, 503, 240, 39),
    "player2ringname": (1000, 535, 378, 35),
    "player1character": (54, 386, 418, 76),
    "player2character": (1004, 386, 418, 76),
    "player1ringname": (75, 540, 378, 28),
    "vs": (586 + 12, 284 + 10, 308 - 45, 154 - 20),
    "ko": (438, 302, 627, 237),
    "excellent": (0, 341, 627, 155),
}

regions_1080p = {
    "player1rank": (162, 204, 37, 28),
    "player2rank": (1842, 204, 37, 28),
    "player1_rounds": (519, 78, 106, 36),
    "player2_rounds": (840, 78, 106, 36),
    "stage": (793, 660, 350, 50),
    "player2ringname": (1000, 535, 378, 35),
    "player1character": (54, 386, 418, 76),
    "player2character": (1004, 386, 418, 76),
    "player1ringname": (75, 540, 378, 28),
    "vs": (790, 383, 350, 186),
    "ko": (438, 302, 627, 237),
    "excellent": (167, 341, 1146, 155),
}

regions_480p = {
    #'player1rank':   (71, 91, 17, 12)
    # ,'player1rank_full': (23, 82, 67, 21)
    "player1rank": (72, 91, 14, 12),
    "player1rank_full": (23, 82, 67, 21),
    "player2rank": (820, 91, 14, 12)
    # ,'player2rank': (819, 91, 14, 12)
    ,
    "player2rank_full": (765, 82, 67, 21),
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
    "time_seconds": (400, 15, 54, 34),
    "time_seconds_digit1": (403, 15, 25, 34),
    "time_seconds_digit2": (427, 15, 25, 34),
    "time_ms": (414, 48, 25, 14),
    "time_ms_digit1": (414, 48, 12, 14),
    "time_ms_digit2": (426, 48, 24, 14),
}

# regions_720p = {
#   'player1rank': (72, 91, 14, 12)
# ,'player2rank': (820, 91, 14, 12)
# ,'player1_rounds': (303, 50, 63, 20)
# ,'player2_rounds': (493, 50, 63, 20)
# ,'stage': (553, 442, 200, 25)
# ,'player1ringname':  (43, 315, 209, 18)
# ,'player2ringname':  (589, 315, 209, 18)
# ,'player1character': (27,   228,   245, 32)
# ,'player2character': (584,  228,   245, 32)
# ,'vs': (343, 173, 172, 85)
# ,'ko': (438, 302, 627, 237)
# ,'excellent': (162, 209, 552, 81)
# }

# 1/3rd of 1080P
regions_360p = {
    "player1rank": (53, 68, 13, 8),
    "stage": (266, 223, 117, 22),
    "player2rank": (614, 68, 13, 8),
    "player1_rounds": (519, 78, 106, 36),
    "player2_rounds": (838, 78, 106, 36),
    "player2ringname": (1000, 535, 378, 35),
    "player1character": (54, 386, 418, 76),
    "player2character": (1004, 386, 418, 76),
    "player1ringname": (75, 540, 378, 28),
    "vs": (260, 125, 117, 63),
    "ko": (438, 302, 627, 237),
    "excellent": (167, 341, 1146, 155),
}

stage_roi = None


def get_player_rank_black(player_num, frame):

    (x, y, w, h) = regions_default[f"player{player_num}rank"]

    roi = frame[y : y + h, x : x + w]

    # cv2.imshow("rank", roi  )
    # cv2.waitKey()

    all_white_roi = all_but_black_range(roi)

    imagem = cv2.bitwise_not(all_white_roi)

    imagem = all_white_roi
    # cv2.rectangle(frame, (x, y), (x+w, y+h), color=(255,0,0), thickness=10)
    # cv2.imshow("rank", frame)
    # cv2.waitKey()

    text = pytesseract.image_to_string(imagem, timeout=2, config="--psm 7")

    # text = str.replace(text, "\n\x0c", "")
    # text = str.replace(text, "\x0c", "")
    # text = str.replace(text, "?", "")
    # text = str.replace(text, "‘", "")

    text = re.sub("[^0-9]", "", text)

    # cv2.imshow("rank", imagem)
    # cv2.waitKey()
    # print(text)

    return int(text)


def load_sample_with_transparency(path):
    # Load the image with transparency
    sample_image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if sample_image is None:
        raise ValueError("Sample image not found")

    return sample_image


def resize_sample_if_needed(sample_image, roi):
    roi_height, roi_width = roi.shape[:2]
    sample_height, sample_width = sample_image.shape[:2]

    if sample_width > roi_width or sample_height > roi_height:
        # print ("resizing")
        scale_width = roi_width / sample_width
        scale_height = roi_height / sample_height
        scale = min(scale_width, scale_height)
        new_width = int(sample_width * scale)
        new_height = int(sample_height * scale)
        sample_image = cv2.resize(
            sample_image, (new_width, new_height), interpolation=cv2.INTER_AREA
        )
    else:
        print(
            f"not resizing cause ${sample_width} ${sample_height} is in ${roi_width} {roi_height}"
        )
    return sample_image


def count_pixels(target_color, image, override_tolerance=40):
    tolerance = override_tolerance  # Adjust this value as needed

    # Convert the target color from hex to BGR
    target_color_bgr = tuple(int(target_color[i : i + 2], 16) for i in (5, 3, 1))

    # Define the lower and upper bounds for the color
    lower_bound = np.array(
        [max(c - tolerance, 0) for c in target_color_bgr], dtype=np.uint8
    )
    upper_bound = np.array(
        [min(c + tolerance, 255) for c in target_color_bgr], dtype=np.uint8
    )

    # Create a mask that identifies all pixels within the color range
    mask = cv2.inRange(image, lower_bound, upper_bound)

    # Count the number of non-zero (white) pixels in the mask
    return cv2.countNonZero(mask)


def all_but_white_strict(roi):
    lower_white = np.array([236, 236, 236])  # Lower bound of white color
    upper_white = np.array([255, 255, 255])  # Upper bound of white color
    mask = cv2.inRange(roi, lower_white, upper_white)

    # Apply the mask to keep only white areas in the ROI
    white_only_roi = cv2.bitwise_and(roi, roi, mask=mask)
    return white_only_roi


def all_but_black_range(roi, low=np.array([0, 0, 0]), high=np.array([120, 120, 120])):
    image_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

    lower_white = low  # Lower bound of white color
    upper_white = high  # Upper bound of white color
    mask = cv2.inRange(image_rgb, lower_white, upper_white)

    # Apply the mask to keep only white areas in the ROI
    # white_only_roi = cv2.bitwise_and(roi, roi, mask=mask)
    return mask


def all_but_black(image):
    image = cv2.bitwise_not(image)
    return vf_cv.CvHelper.all_but_white(image)


def all_but_grey(roi):
    lower_white = np.array([165, 165, 165])  # Lower bound of white color
    upper_white = np.array([255, 255, 255])  # Upper bound of white color
    mask = cv2.inRange(roi, lower_white, upper_white)

    # Apply the mask to keep only white areas in the ROI
    white_only_roi = cv2.bitwise_and(roi, roi, mask=mask)
    return white_only_roi


def get_ringname(player_num, frame, region_override=None):
    return "n/a"


def get_dimensions(region_name, local_resolution, override_region=None):
    (x, y, w, h) = (0, 0, 0, 0)

    if override_region is not None:
        (x, y, w, h) = override_region[region_name]
    elif local_resolution == "480p":
        (x, y, w, h) = regions_480p[region_name]
    elif local_resolution == "720p":
        (x, y, w, h) = regions_480p[region_name]
        x = (int)(x * 1.5)
        y = (int)(y * 1.5)
        w = (int)(w * 1.5)
        h = (int)(h * 1.5)
    return (x, y, w, h)

def get_stage_roi(frame):
    region_name = "stage"

    height = frame.shape[0]  # Get the dimensions of the frame
    (x, y, w, h) = get_dimensions(region_name, f"{height}p")

    factor = 1.0

    if height == 720:
        factor = 1.5

    x = int(x * factor)
    y = int(y * factor)
    w = int(w * factor)
    h = int(h * factor)

    roi = frame[y : y + h, x : x + w]

    all_white_roi = all_but_grey(roi)

    imagem = cv2.bitwise_not(all_white_roi)
    return imagem

def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized


def remove_black_border(image, threshold_value=10, resize_height=None):
    if image is None:
        raise Exception("cannot remove black border, image is null")
    # Convert to grayscale and threshold
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the bounding box of the largest contour
    if contours:
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        cropped_image = image[y : y + h, x : x + w]
        cropped_image = cv2.resize(cropped_image, (854, 480))

        if resize_height is not None:
            height, width, channels = cropped_image.shape
            if height != resize_height and resize_height == 480:
                cropped_image = cv2.resize(cropped_image, (854, 480))

        return cropped_image

    return image
