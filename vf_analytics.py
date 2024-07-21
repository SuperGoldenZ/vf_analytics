import cv2
import numpy as np
import pytesseract
import re
import logging

# PS4 Resolution is 1920 x 1080 1080P

logger = logging.getLogger(__name__)
logging.basicConfig(filename='analyze_youtube.log', encoding='utf-8', level=logging.DEBUG)

resolution='1080p'

#alexRegions
regions_default = {
    'player1rank': (125, 156, 22, 18)
    ,'player2rank': (1410, 158, 22, 18)
    ,'player1_rounds': (519, 78, 106, 36)
    ,'player2_rounds': (840, 78, 106, 36)
    ,'stage': (619, 503, 240, 39)
    ,'player2ringname':  (1000, 535, 378, 35)
    ,'player1character': (54,    386,   418, 76)
    ,'player2character': (1004,  386,    418, 76)
    ,'player1ringname':  (75, 540, 378, 28)
    ,'vs': (586+12, 284+10, 308-45, 154-20)
    ,'ko': (438, 302, 627, 237)
    ,'excellent': (0, 341, 627, 155)
}

regions_1080p = {
    'player1rank': (162, 204, 37, 28)
    ,'player2rank': (1842, 204, 37, 28)
    ,'player1_rounds': (519, 78, 106, 36)
    ,'player2_rounds': (840, 78, 106, 36)
    ,'stage': (793, 660, 350, 50)
    ,'player2ringname':  (1000, 535, 378, 35)
    ,'player1character': (54,    386,   418, 76)
    ,'player2character': (1004,  386,    418, 76)
    ,'player1ringname':  (75, 540, 378, 28)
    ,'vs': (790, 383, 350, 186)
    ,'ko': (438, 302, 627, 237)
    ,'excellent': (167, 341, 1146, 155)
}

regions_480p = {
    'player1rank': (72, 91, 14, 12)
    ,'player2rank': (820, 91, 14, 12)
    ,'player1_rounds': (303, 50, 63, 20)
    ,'player2_rounds': (493, 50, 63, 20)
    ,'player2_rounds1': (493, 50, 25, 20)
    ,'stage': (342, 295, 200, 25)
    ,'player1ringname':  (43, 315, 209, 18)
    ,'player2ringname':  (589, 315, 209, 18)
    ,'player1character': (27,   228,   245, 32)
    ,'player2character': (584,  228,   245, 32)
    ,'vs': (343, 173, 172, 85)
    ,'ko': (250, 170, 350, 140)
    ,'excellent': (75, 200, 275, 80)
    ,'ro': (185, 204, 484, 80)
}

#regions_720p = {
 #   'player1rank': (72, 91, 14, 12)
    #,'player2rank': (820, 91, 14, 12)
    #,'player1_rounds': (303, 50, 63, 20)
    #,'player2_rounds': (493, 50, 63, 20)
    #,'stage': (553, 442, 200, 25)
    #,'player1ringname':  (43, 315, 209, 18)
    #,'player2ringname':  (589, 315, 209, 18)
    #,'player1character': (27,   228,   245, 32)
    #,'player2character': (584,  228,   245, 32)
    #,'vs': (343, 173, 172, 85)
    #,'ko': (438, 302, 627, 237)
    #,'excellent': (162, 209, 552, 81)
#}

# 1/3rd of 1080P
regions_360p = {
    'player1rank': (53, 68, 13, 8)
    ,'stage': (266, 223, 117, 22)
    ,'player2rank': (614, 68, 13, 8)
    ,'player1_rounds': (519, 78, 106, 36)
    ,'player2_rounds': (838, 78, 106, 36)
    ,'player2ringname':  (1000, 535, 378, 35)
    ,'player1character': (54,    386,   418, 76)
    ,'player2character': (1004,  386,    418, 76)
    ,'player1ringname':  (75, 540, 378, 28)
    ,'vs': (260, 125, 117, 63)
    ,'ko': (438, 302, 627, 237)
    ,'excellent': (167, 341, 1146, 155)
}

# min width 25
def get_player_rank(player_num, frame, retry=0, override_regions=None):
    if (retry > 6):
        return 0

    region_name=f"player{player_num}rank"
    (x, y, w, h) = get_dimensions(region_name, resolution, override_regions)

    if (retry == 1):
        w = w -3
        x = x + 2
    elif (retry ==2):
        x = x - 29
        y = y - 10
    elif (retry ==3  and override_regions != regions_360p):
        x = x + 29
        y = y - 10
    elif (retry ==4  and override_regions != regions_360p):
        x = x - 20
        y = y - 10
    elif (retry ==5 and override_regions != regions_360p):
        x = x + 26
        y = y - 8
    elif (retry == 6 and player_num == 1):
        w = w + 10
    elif (retry == 6 and player_num == 2):
        x = x - 5
        w = w + 5
        h = h + 3


    roi = frame[y:y+h, x:x+w]

    white_count = count_pixels("#000000", roi, 50)
    #print(f"white count {white_count}")
    all_white_roi = all_but_white_vftv(roi, np.array([100, 100, 105]))

    imagem = cv2.bitwise_not(all_white_roi)

    #cv2.rectangle(frame, (x, y), (x+w, y+h), color=(255,0,0), thickness=10)
    #cv2.imshow("rank", all_white_roi)
    #cv2.waitKey()


    text = pytesseract.image_to_string(imagem, timeout=2, config="--psm 7")

    #text = str.replace(text, "\n\x0c", "")
    #text = str.replace(text, "\x0c", "")
    #text = str.replace(text, "?", "")
    #text = str.replace(text, "‘", "")

    text = re.sub("[^0-9]", "", text)

    #cv2.imshow("roi", roi)
    #cv2.imshow("rank", imagem)
    #print(f"{text} for {player_num} player")
    #cv2.waitKey()

    if (not text.isnumeric() or int(text) < 10):
        return get_player_rank(player_num, frame, retry=retry+1, override_regions=override_regions);

    greyCount = count_pixels("#7c7a82", roi)

    rank_int = int(text)
    if (rank_int == 38 and white_count == 8):
        return 39

    if (rank_int > 46 and retry < 3):
        return get_player_rank(player_num, frame, retry=retry+1, override_regions=override_regions)

    if (rank_int >= 40 and greyCount > 130) and rank_int <= 56:
        return (int(text)-10)

    if (rank_int < 0 or rank_int > 46):
        return 0

    return rank_int

def get_player_rank_black(player_num, frame):

    (x, y, w, h) = regions_default[f"player{player_num}rank"]

    roi = frame[y:y+h, x:x+w]

    #cv2.imshow("rank", roi  )
    #cv2.waitKey()

    all_white_roi = all_but_black_range(roi)

    imagem = cv2.bitwise_not(all_white_roi)

    imagem = all_white_roi
    #cv2.rectangle(frame, (x, y), (x+w, y+h), color=(255,0,0), thickness=10)
    #cv2.imshow("rank", frame)
    #cv2.waitKey()



    text = pytesseract.image_to_string(imagem, timeout=2, config="--psm 7")

    #text = str.replace(text, "\n\x0c", "")
    #text = str.replace(text, "\x0c", "")
    #text = str.replace(text, "?", "")
    #text = str.replace(text, "‘", "")

    text = re.sub("[^0-9]", "", text)

    #cv2.imshow("rank", imagem)
    #cv2.waitKey()
    #print(text)

    return int(text)

def load_sample_with_transparency(path):
    # Load the image with transparency
    sample_image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if sample_image is None:
        raise ValueError("Sample image not found")

    return sample_image

def is_vs_text(text):
    text = text.strip()

    if (len(text) > 20):
        return False
    if ("Wiss" in text):
        return True
    if ("WV" in text):
        return True
    if ("WIS" in text):
        return True
    if ("WES" in text):
        return True
    if ("WAS" in text):
        return True
    if ("NS" in text):
        return True
    if ("WS" in text):
        return True
    if ("VS" in text):
        return True
    if ("AS" in text):
        return True
    return False

#min width = 50
def is_vs(frame, retry = 0, override_regions = None):
    if (retry == 4):
        return False

    (x, y, w, h) = (0, 0, 0, 0)

    if (override_regions is not None):
        (x, y, w, h) = override_regions["vs"]
    elif (resolution == '480p'):
        (x, y, w, h) = regions_480p["vs"]

    if (retry == 1):
        x += 8
        y += 3
        w -= 13
        h -= 8
    if (retry == 2):
        x -= 20
        y -= 20
        w += 30
        h += 30
    if (retry == 3):
        x += 8
        #y += 8
        w -= 15
        h -= 8

    roi = frame[y:y+h, x:x+w]

    #black_pixel_count = count_pixels("#090803", roi)
    #grey_pixel_count = count_pixels("#76716d", roi)
    #if (grey_pixel_count > 3000 and grey_pixel_count < 3400 and
        #black_pixel_count > 2000 and black_pixel_count < 2500
        #):
        #return True

    #print(f"black: {black_pixel_count} grey: {grey_pixel_count}")


    all_black_roi = all_but_black_range(roi,
        np.array([0,0,0]),
        np.array([25,25,15])
        )

    #if (retry == 0):
        #all_white_roi = image_resize(all_white_roi, width=50)

    text = pytesseract.image_to_string(all_black_roi, config="--psm 7")
    if (is_vs_text(text)):
        return True

    all_white_roi = all_but_black_range(roi,
            np.array([100,100,100]),
            np.array([255,255,255])
    )

    text = pytesseract.image_to_string(all_white_roi, config="--psm 7")
    if (is_vs_text(text)):
        return True

    blue_pixel_count = count_pixels("#0b0e91", roi)
    red_pixel_count = count_pixels("#880807", roi)


    if (blue_pixel_count > 500):
        return False

    #if (red_pixel_count > 500):
        #return False

    grey_pixels = count_pixels('#a4a09a', roi)
    white_pixels = count_pixels('#fffffb', roi)

    #if (grey_pixels > 5700 and grey_pixels < 6000 and
        #white_pixels > 2300 and white_pixels < 2600
        #):
        #return True

    return is_vs(frame, retry+1, override_regions)

def is_ko(frame, override_region=None):
    region_name='ko'
    (x, y, w, h) = get_dimensions(region_name, resolution, override_region)

    roi = frame[y:y+h, x:x+w]
    #lower_bound = np.array([77, 78, 78])  # BGR for #c58e4d
    #upper_bound = np.array([255, 255, 255])  # BGR for #ffffff
    #isolated = isolate_color_range(roi, lower_bound, upper_bound)
    #text = pytesseract.image_to_string(roi, config="--psm 6")

    gold_count = count_pixels('#ce9e54', roi, override_tolerance=5)
    red_count = count_pixels('#b3200e', roi, override_tolerance=25)
    purple_count = count_pixels('#422fc9', roi, override_tolerance=25)
    black_count = count_pixels('#000000', roi, override_tolerance=25)
    white_count = count_pixels('#FFFFFF', roi, override_tolerance=25)

    logger.debug(f"\tko count gold {gold_count} red {red_count} purple{purple_count} black {black_count} white {white_count} resolution {resolution}")
    #cv2.imshow("is_ko frame", frame)
    #cv2.imshow("is_ko roi", roi)
    #cv2.waitKey()

    if (resolution == "480p"):
        if (purple_count > 140 and black_count > 200):
            return False
        if (gold_count > 10 and white_count > 7000):
            return True
        if (white_count > 14000):
            return True
        if (gold_count > 42 and purple_count > 10):
            return True

    return False

def is_excellent(frame, override_region=None):
    region_name="excellent"
    (x, y, w, h) = get_dimensions(region_name, resolution, override_region)

    roi = frame[y:y+h, x:x+w]

    white_count = count_pixels('#ffffff', roi, override_tolerance=5)
    gold_count = count_pixels('#ce9e54', roi, override_tolerance=5)
    red_count = count_pixels('#b3200e', roi, override_tolerance=25)
    purple_count = count_pixels('#422fc9', roi, override_tolerance=25)
    black_count = count_pixels('#000000', roi, override_tolerance=25)

    logger.debug(f"\nexcellent white count {white_count} gold {gold_count} red {red_count} purple {purple_count} black {black_count}")

    #cv2.imshow("excellent", frame)
    #cv2.imshow("excellent", roi)
    #cv2.waitKey()

    if (is_ko(frame)):
        return False

    if (resolution == "480p"):
        #excellent excellent white count 118 gold 88 red 0 purple 10 black 1090
        #not excellent white count 750 gold 32 red 347 purple 520 black 175

        # not excellent
        #if (white_count < 105 and gold_count < 150 and black_count < 500):
            #return False
        #excellent white count 229 gold 60 red 0 purple 10 black 261
        #if (white_count > 200 and gold_count < 70):
            #return False

        if (white_count > 2500):
            return False

        if (red_count > 150 and purple_count > 50):
            return False

        if (white_count > 15 and black_count > 45):
            return True

        if (white_count > 18 and black_count == 0 and red_count == 0 and gold_count == 0):
            return True

        if (gold_count > 25 and red_count > 45 and black_count > 45):
            return True

        if (gold_count < 150 and white_count > 91 and black_count < 1800 and white_count < 250 and purple_count < 200 and black_count > 45):
            return True

        if (gold_count > 85 and red_count > 50 and black_count > 45):
            return True

    return False

def is_ringout(frame, override_region=None):
    region_name="ro"
    (x, y, w, h) = get_dimensions(region_name, resolution, override_region)

    roi = frame[y:y+h, x:x+w]

    green_count = count_pixels('#07a319', roi, override_tolerance=15)
    black_count = count_pixels('#000000', roi, override_tolerance=15)
    white_count = count_pixels('#FFFFFF', roi, override_tolerance=15)

    #print(f"is_ringout green {green_count} black {black_count} white {white_count}")
    #cv2.imshow("ro frame", frame)
    #cv2.imshow("ro roi", roi)
    #cv2.waitKey()
    return green_count > 400

def resize_sample_if_needed(sample_image, roi):
    roi_height, roi_width = roi.shape[:2]
    sample_height, sample_width = sample_image.shape[:2]

    if sample_width > roi_width or sample_height > roi_height:
        print ("resizing")
        scale_width = roi_width / sample_width
        scale_height = roi_height / sample_height
        scale = min(scale_width, scale_height)
        new_width = int(sample_width * scale)
        new_height = int(sample_height * scale)
        sample_image = cv2.resize(sample_image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    else:
        print (f"not resizing cause ${sample_width} ${sample_height} is in ${roi_width} {roi_height}")
    return sample_image

def count_pixels(target_color, image, override_tolerance=40):
    tolerance = override_tolerance  # Adjust this value as needed

        # Convert the target color from hex to BGR
    target_color_bgr = tuple(int(target_color[i:i+2], 16) for i in (5, 3, 1))

    # Define the lower and upper bounds for the color
    lower_bound = np.array([max(c - tolerance, 0) for c in target_color_bgr], dtype=np.uint8)
    upper_bound = np.array([min(c + tolerance, 255) for c in target_color_bgr], dtype=np.uint8)

    # Create a mask that identifies all pixels within the color range
    mask = cv2.inRange(image, lower_bound, upper_bound)

    # Count the number of non-zero (white) pixels in the mask
    return cv2.countNonZero(mask)


def count_rounds_won(frame, playerNumber, override_region=None, wonSoFar=0):
    #Rounds won
    region_name=f"player{playerNumber}_rounds"
    #if (wonSoFar == 0 and playerNumber == 2):
        #region_name=f"player{playerNumber}_rounds1"
    (x, y, w, h) = get_dimensions(region_name, resolution, override_region)
    roi = frame[y:y+h, x:x+w]

    #Excellent
    region_name="excellent"
    (x, y, w, h) = get_dimensions(region_name, resolution, override_region)
    excellent = frame[y:y+h, x:x+w]

    gold_count = count_pixels("#a08747", excellent)
    red_count = count_pixels("#a72027", excellent)
    purple_count = count_pixels("#2d0c5b", excellent)
    white_count = count_pixels("#ffffff", excellent, 5)

    #cv2.imshow("wzxl", excellent)
    #cv2.waitKey()

    #if (gold_count > 3000 and red_count > 1000 and purple_count > 1000):
        #raise Exception("Round start")

    if (not is_excellent(frame) and not is_ko(frame) and not is_ringout(frame)):
        logger.debug("\traising exception because not found end of round test")
        raise Exception("Not sure how won")

    # Convert BGR to HSV
    #hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    grey_pixel_count = count_pixels("#aea6a4", roi)

    # Define range of red color in HSV
    if (playerNumber == 1):
        red_pixel_count = count_pixels("#e02958", roi)
        logger.debug(f"\trounds won Player 1  - Red count: {red_pixel_count} - Grey Count: {grey_pixel_count} So Far: {wonSoFar}")

        #cv2.imshow("roi", roi)
        #cv2.waitKey()

        if (override_region == regions_480p or resolution == '480p'):
            if (wonSoFar == 2 and red_pixel_count > 135 and grey_pixel_count < 100):
                return 3

            if (wonSoFar == 1 and red_pixel_count > 135):
                return 2

            if (red_pixel_count > 290):
                return 0

            if (red_pixel_count > 210):
                return 3

            if (red_pixel_count > 135 and grey_pixel_count >= 90):
                return 2

            if (red_pixel_count > 140 and grey_pixel_count < 35):
                return 1

            if (red_pixel_count > 70):
                return 1

            if (red_pixel_count > 60 and grey_pixel_count > 250):
                return 1


        if (resolution == '720p'):
            if (red_pixel_count > 290*1.5):
                return 0

            if (red_pixel_count > 210*1.5):
                return 3

            if (red_pixel_count > 135*1.5 and grey_pixel_count >= 90*1.5):
                return 2

            if (red_pixel_count > 140*1.5 and grey_pixel_count < 35*1.5):
                return 1

            if (red_pixel_count > 70*1.5):
                return 1

        if (red_pixel_count > 700):
            return 3

        if (red_pixel_count > 380):
            return 2

        if (red_pixel_count >= 231):
            return 1

    else:
        #ce9e54

        target_color = '#0d6ed7'  # Blue color
        blue_count = count_pixels(target_color, roi)
        white_count = count_pixels("#FFFFFF", roi)

        logger.debug(f"\trounds won player 2 blue count {blue_count}  white {white_count} grey {grey_pixel_count} sofar {wonSoFar}")

        #cv2.imshow("frame", frame)
        #cv2.imshow("roi", roi)
        #cv2.waitKey()


        if (override_region == regions_480p or resolution == '480p'):

            if (wonSoFar == 0 and white_count > 65):
                logger.debug("returning 1 for white_count and wonSoFar")
                return 1

            if (blue_count > 290):
                return 0

            if (blue_count > 56 and grey_pixel_count < 90):
                return 3

            if (blue_count > 60 and grey_pixel_count > 270):
                return 2

            if (white_count > 230 and white_count < 260):
                return 2

            if (blue_count > 70 and grey_pixel_count < 230):
                return 2

            if (blue_count > 60 and grey_pixel_count < 107):
                return 2

            if (blue_count > 40 and grey_pixel_count < 94):
                return 2

            if (blue_count > 40 and grey_pixel_count < 75):
                return 2

            if (blue_count > 40 and grey_pixel_count < 130):
                return 1

            if (blue_count > 20):
                return 1

        if (resolution == '720p'):
            if (blue_count > 290*1.5):
                return 0

            if (blue_count > 60*1.5 and grey_pixel_count < 90*1.5):
                return 3

            if (blue_count > 60*1.5 and grey_pixel_count > 270*1.5):
                return 2

            if (blue_count > 60*1.5 and grey_pixel_count < 100*1.5):
                return 2

            if (blue_count > 40*1.5 and grey_pixel_count < 94*1.5):
                return 2

            if (blue_count > 40*1.5 and grey_pixel_count < 75*1.5):
                return 2

            if (blue_count > 40*1.5 and grey_pixel_count < 130*1.5):
                return 1

            if (blue_count > 20):
                return 1

        if (blue_count > 305):
            return 3

        if (blue_count > 200):
            return 2

        if (blue_count > 100):
            return 1


    return 0

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

def all_but_white(roi):
    lower_white = np.array([230, 230, 230])  # Lower bound of white color
    upper_white = np.array([255, 255, 255])  # Upper bound of white color
    mask = cv2.inRange(roi, lower_white, upper_white)

    # Apply the mask to keep only white areas in the ROI
    white_only_roi = cv2.bitwise_and(roi, roi, mask=mask)
    return white_only_roi

def all_but_white_strict(roi):
    lower_white = np.array([236, 236, 236])  # Lower bound of white color
    upper_white = np.array([255, 255, 255])  # Upper bound of white color
    mask = cv2.inRange(roi, lower_white, upper_white)

    # Apply the mask to keep only white areas in the ROI
    white_only_roi = cv2.bitwise_and(roi, roi, mask=mask)
    return white_only_roi

def all_but_black_range(roi, low = np.array([0,0,0]), high=np.array([120,120,120])):
    image_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

    lower_white = low  # Lower bound of white color
    upper_white = high  # Upper bound of white color
    mask = cv2.inRange(image_rgb, lower_white, upper_white)

    # Apply the mask to keep only white areas in the ROI
    #white_only_roi = cv2.bitwise_and(roi, roi, mask=mask)
    return mask


def all_but_black(image):
    image = cv2.bitwise_not(image)
    return all_but_white(image)

    inverted_image = PIL.ImageOps.invert(image)
    lower_white = np.array([0, 0, 0])  # Lower bound of white color
    upper_white = np.array([1, 1, 1])  # Upper bound of white color
    mask = cv2.inRange(image, lower_white, upper_white)
    return mask
    # Apply the mask to keep only white areas in the ROI
    #white_only_roi = cv2.bitwise_and(image, image, mask=mask)

    # Convert to grayscale (optional, if your image is colored)
    #gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Create a mask where black pixels are identified (thresholding)
    # The threshold can be adjusted if needed; here we assume an intensity of 0 is black
    #_, mask = cv2.threshold(image, 2, 255, cv2.THRESH_BINARY_INV)

    # Create an output image, initialized to white
    #output = np.ones_like(image) * 255

    # Copy the black pixels from the original image to the output image using the mask
    #output[mask == 255] = image[mask == 255]

    return output

def all_but_grey(roi):
    lower_white = np.array([165, 165, 165])  # Lower bound of white color
    upper_white = np.array([255, 255, 255])  # Upper bound of white color
    mask = cv2.inRange(roi, lower_white, upper_white)

    # Apply the mask to keep only white areas in the ROI
    white_only_roi = cv2.bitwise_and(roi, roi, mask=mask)
    return white_only_roi

def all_but_white_vftv(roi, lower=np.array([100, 100, 100])):
    lower_white = lower  # Lower bound of white color
    upper_white = np.array([255, 255, 255])  # Upper bound of white color
    mask = cv2.inRange(roi, lower_white, upper_white)

    # Apply the mask to keep only white areas in the ROI
    white_only_roi = cv2.bitwise_and(roi, roi, mask=mask)
    return white_only_roi

def get_ringname(player_num, frame, region_override=None):
    region_name=f"player{player_num}ringname"

    (x, y, w, h) = get_dimensions(region_name, resolution, region_override)

    roi = frame[y:y+h, x:x+w]

    all_white_roi = all_but_grey(roi)
    imagem = cv2.bitwise_not(all_white_roi)

    text = pytesseract.image_to_string(imagem, config="--psm 6")
    text = str.replace(text, "\n\x0c", "")
    text = str.replace(text, " ", "")
    text = str.replace(text, "‘", "")
    text = str.replace(text, ":", "-")
    text = str.replace(text, "{", "")
    text = str.replace(text, "|", "")
    text = str.replace(text, ",", "")
    text = str.replace(text, "?", "")
    text = str.replace(text, "(", "")
    text = str.replace(text, ")", "")
    text = str.replace(text, "}", "")
    text = str.replace(text, "{", "")
    text = str.replace(text, "!", "")
    text = str.replace(text, "”", "")

    if ("\"" in text):
        return "n/a"

    if ("\n" in text):
        return "n/a"

    if ("=" in text):
        return "n/a"

    if (len(text) >= 3):
        return text

    return "n/a"

def get_dimensions(region_name, resolution, override_region=None):
    (x, y, w, h) = (0, 0, 0, 0)

    if (override_region is not None):
        (x, y, w, h) = override_region[region_name]
    elif (resolution == '480p'):
        (x, y, w, h) = regions_480p[region_name]
    elif (resolution == '720p'):
        (x, y, w, h) = regions_480p[region_name]
        x = (int) (x * 1.5)
        y = (int) (y*1.5)
        w = (int) (w*1.5)
        h = (int) (h*1.5)
    return (x, y, w, h)

# Min width of frame is 85
def get_stage(frame, override_region=None):
    region_name="stage"
    (x, y, w, h) = get_dimensions(region_name, resolution, override_region)
    roi = frame[y:y+h, x:x+w]

    all_white_roi = all_but_grey(roi)
    #all_white_roi = image_resize(all_white_roi, width = 85)

    imagem = cv2.bitwise_not(all_white_roi)

    text = pytesseract.image_to_string(imagem, config="--psm 6")
    text = str.replace(text, "\n\x0c", "").upper()

    #cv2.imshow("original: ", frame)
    #cv2.imshow("roi", roi)
    #print(f"{text} for resolution {resolution}")
    #cv2.waitKey()

    if (text == "WATER FALLS"):
        return "Waterfalls"

    if (text == "ISLAND"):
        return "Island"

    if (text == "SSFAND"):
        return "Island"

    if (text == "TAMPIA"):
        return "Temple"

    if ("ARENA" == text):
        return "Arena"

    if ("PALCE" == text):
        return "Palace"

    if ("AURORA" == text):
        return "Aurora"

    if ("TEMPLE" == text):
        return "Temple"

    if ("SUMO RING" == text):
        return "Sumo Ring"

    if ("RUINS" == text):
        return "Ruins"

    if ("STATUES" == text):
        return "Statues"

    if ("GREAT WALL" == text):
        return "Great Wall"

    if ("WALL" in text):
        return "Great Wall"

    if ("CITY" == text):
        return "City"

    if ("TERRACE" == text):
        return "Terrace"

    if ("RIVER" == text):
        return "River"

    if ("FALL" in text):
        return "Waterfalls"

    if ("WATER" in text):
        return "Waterfalls"

    if ("WATERFALLS" in text):
        return "Waterfalls"

    if ("GRASS" in text):
        return "Grassland"

    if ("DEEP" in text):
        return "Deep Mountain"

    if ("BROKEN" in text or "House" in text):
        return "Broken House"

    if ("GENESIS" == text):
        return "Genesis"

    if ("SHRINE" == text):
        return "Shrine"

    if (text == "TRAINING ROOM"):
        return "Training Room"

    if ("SNOW" in text):
        return "Snow Mountain"

    if ("PALACE" in text):
        return "Palace"

    if ("TEMPLE" in text):
        return "Temple"

    if ("RUINS" in text):
        return "Ruins"

    return None

def get_character_name(player_num, frame, retry=0, override_region=None):
    region_name = f"player{player_num}character"

    (x, y, w, h) = get_dimensions(region_name, resolution, override_region)

    if (retry == 1 and player_num == 1):
        w = w - 75
        h = h - 15
    elif (retry == 1 and player_num == 2):
        x = x - 20
        w = w + 20

    if (retry == 2 and player_num == 1):
        x = x + 20
        w = w - 100
        h = h - 20
    elif (retry == 2 and player_num == 2):
        x = x + 50
        w = w - 100

    if (retry == 3 and player_num == 1):
        x = x + 20
        w = w - 100
        h = h - 20
    elif (retry == 3 and player_num == 2):
        x = x + 175
        w = w - 175
        y = y + 10
        h = h - 10

    roi = frame[y:y+h, x:x+w]


    white_only_roi = all_but_white(roi)
    text = pytesseract.image_to_string(white_only_roi, config="--psm 6")

    #print(text)
    #cv2.imshow("roi", white_only_roi)
    #cv2.waitKey()

    if ("Brad" in text):
        text="Brad"
    if ("Kage" in text):
        text="Kage"
    if ("Akira" in text):
        text = "Akira"
    if ("Blaze" in text):
        text = "Blaze"
    if ("Wolf" in text):
        text = "Wolf"
    if ("Lei" in text):
        return "Lei Fei"
    if ("Aoi" in text):
        return "Aoi"
    if ("Akira" in text):
        return "Akira"
    if ("Jean" in text):
        return "Jean"
    if ("Lau" in text):
        return "Lau"
    if ("Taka" in text):
        return "Taka"
    if ("Sarah" in text):
        return "Sarah"
    if ("Jacky" in text):
        return "Jacky"
    if ("Shun" in text):
        return "Shun"
    if ("Goh" in text):
        return "Goh"
    if ("Lion" in text):
        return "Lion"
    if ("Vanessa" in text):
        return "Vanessa"
    if ("Jeffry" in text):
        return "Jeffry"
    if ("Pai" in text):
        return "Pai"
    if ("Goh" in text):
        return "Goh"
    if ("Eileen" in text):
        return "Eileen"

    if (text == "EI Blaze"):
        text = "Blaze"

    if (is_vf_character_name(text)):
        return str.replace(text, "\n\x0c", "")

    if (retry < 3):
        return get_character_name(player_num, frame, retry+1, override_region)
    return None

def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
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
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized

def remove_black_border(image, threshold_value = 10):
    # Convert to grayscale and threshold
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the bounding box of the largest contour
    if contours:
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        cropped_image = image[y:y+h, x:x+w]
        cropped_image = cv2.resize(cropped_image, (854, 480))

        #cv2.imshow("crpoped image", cropped_image)
        #cv2.waitKey()
        return cropped_image

    return image

def isolate_color_range(image, lower_bgr, upper_bgr):
  # Convert BGR bounds to HSV
    lower_hsv = cv2.cvtColor(np.uint8([[lower_bgr]]), cv2.COLOR_BGR2HSV)[0][0]
    upper_hsv = cv2.cvtColor(np.uint8([[upper_bgr]]), cv2.COLOR_BGR2HSV)[0][0]

    # Convert the image to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Create a mask using the bounds
    mask = cv2.inRange(hsv_image, lower_hsv, upper_hsv)

    # Create an output image with the mask applied
    output_image = cv2.bitwise_and(image, image, mask=mask)

    return mask
