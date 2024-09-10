import re
import logging
import cv2
import numpy as np
import pytesseract
import vf_cv

# PS4 Resolution is 1920 x 1080 1080P

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="vf_analytics.log",
    encoding="utf-8",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
)

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


IS_VS_RED_COORDINATES = {
    480: [91, 21],
    720: [int(91 * 1.5), int(21 * 1.5)],
    1080: [int(91 * 2.25), int(21 * 2.25)],
}

IS_VS_BLUE_COORDINATES = {
    480: [91, 847],
    720: [int(91 * 1.5), int(847 * 1.5)],
    1080: [int(91 * 2.25), int(847 * 2.25)],
}

IS_P2_BLUE_COORDINATES = {
    480: [296, 587],
    720: [int(296 * 1.5), int(587 * 1.5)],
    1080: [int(296 * 2.25), int(587 * 2.25)],
}

VS_GRAY_COORDINATES = {
    480: [186, 369],
    720: [int(186 * 1.5), int(369 * 1.5)],
    1080: [int(186 * 2.25), int(369 * 2.25)],
}

VS_BLACK_COORDINATES = {
    480: [178, 363],
    720: [int(178 * 1.5), int(363 * 1.5)],
    1080: [int(178 * 2.25), int(363 * 2.25)],
}


def is_vs(frame, debug=False):
    height = frame.shape[0]  # Get the dimensions of the frame

    result = True

    debug_message = "is_vs roi"
    r1 = frame[IS_VS_RED_COORDINATES[height][0], IS_VS_RED_COORDINATES[height][1]][2]
    r2 = frame[
        IS_VS_RED_COORDINATES[height][0] + 25, IS_VS_RED_COORDINATES[height][1] + 75
    ][2]

    if r1 < 80 and r2 < 80:
        debug_message = f"{debug_message} false 1"
        result = False
    else:
        b1 = frame[
            IS_VS_BLUE_COORDINATES[height][0], IS_VS_BLUE_COORDINATES[height][1]
        ][0]
        b2 = frame[
            IS_VS_BLUE_COORDINATES[height][0] + 25,
            IS_VS_BLUE_COORDINATES[height][1] - 125,
        ][0]
        frame[
            IS_VS_BLUE_COORDINATES[height][0] + 25,
            IS_VS_BLUE_COORDINATES[height][1] - 125,
        ] = (0, 255, 0)

        if b1 < 80 and b2 < 80:
            debug_message = f"{debug_message} false 2"
            result = False
        else:
            (b, g, r) = frame[
                IS_P2_BLUE_COORDINATES[height][0], IS_P2_BLUE_COORDINATES[height][1]
            ]
            if b < 80:
                debug_message = f"{debug_message} false 3"
                result = False
            else:
                (b, g, r) = frame[
                    VS_GRAY_COORDINATES[height][0], VS_GRAY_COORDINATES[height][1]
                ]
                if b < 90 or g < 90 or r < 90:
                    debug_message = f"{debug_message} false 4"
                    result = False
                else:
                    (b, g, r) = frame[
                        VS_BLACK_COORDINATES[height][0], VS_BLACK_COORDINATES[height][1]
                    ]
                    if b > 40 or g > 40 or r > 40:
                        debug_message = f"{debug_message} false 5"
                        result = False

    if debug:
        cv2.imshow(debug_message, frame)
        cv2.waitKey()

    return result


# Min width of frame is 85
def get_stage(frame, override_region=None):
    region_name = "stage"
    (x, y, w, h) = get_dimensions(region_name, resolution, override_region)

    factor = 1.0

    height = frame.shape[0]  # Get the dimensions of the frame

    if height == 720:
        factor = 1.5

    x = int(x * factor)
    y = int(y * factor)
    w = int(w * factor)
    h = int(h * factor)

    roi = frame[y : y + h, x : x + w]

    if False:

        gray_image = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        threshold_value = 15
        _, thresholded_frame = cv2.threshold(
            gray_frame, threshold_value, 255, cv2.THRESH_BINARY
        )

        # gray_frame = frame
        # (r,g,b) = gray_frame[25, 50]

        # color = thresholded_frame[0, 50]
        # thresholded_frame[25, 50] = 255

        threshold_value = 225
        _, thresholded_image = cv2.threshold(
            gray_image, threshold_value, 255, cv2.THRESH_BINARY
        )

        n_white_pix = np.sum(thresholded_image == 255)

        frame[0, 100] = (255, 0, 0)
        thresholded_frame[0:0, 100:100] = 200

        # print(f"{r} {g} {b}")

        # cv2.imshow("frame", frame)
        # cv2.imshow("thres_frame", thresholded_frame)
        # cv2.imshow("threshold", thresholded_image)
        # print(f"for resolution {resolution} white count {n_white_pix}")
        # cv2.waitKey()

        # if (thresholded_frame[0, 0] == 0 and thresholded_frame[height-1, 0] == 0 and
        # thresholded_frame[height-1, width-1] == 0 and thresholded_frame[0, width-1] == 0):
        # return None
        (b, g, r) = frame[202, 377]
        if r < 45 and g < 45 and b < 45:
            return None

        (b, g, r) = frame[178, 365]
        if r > 45 and g > 45 and b > 45:
            return None

        if height == 720 and 1439 - 10 <= n_white_pix <= 1439 + 10:
            return "Deep Mountain"

        if height == 480 and (587 - 10) * factor <= n_white_pix <= (587 + 10) * factor:
            return "Deep Mountain"

        # if (310 <= n_white_pix <= 365):
        # return "Island"

        if 510 <= n_white_pix <= 525:
            return "Sumo Ring"

        if 590 <= n_white_pix <= 600:
            return "Training Room"

        if 370 <= n_white_pix <= 390:
            return "Genesis"

        if 220 <= n_white_pix <= 245:
            return "City"

        if 490 <= n_white_pix <= 510:
            return "Snow Mountain"

        if 340 <= n_white_pix <= 350:
            return "Terrace"

        # if (560 <= n_white_pix <= 580):
        # return "Waterfalls"
    # raise Exception ("oh noes stage")
    # return None

    all_white_roi = all_but_grey(roi)

    imagem = cv2.bitwise_not(all_white_roi)

    text = pytesseract.image_to_string(imagem, config="--psm 6")
    text = str.replace(text, "\n\x0c", "").upper()

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

    if "STATUES" == text:
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
