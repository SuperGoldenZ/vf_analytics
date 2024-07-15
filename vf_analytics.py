import cv2
import numpy as np
import pytesseract
import re
import logging

# PS4 Resolution is 1920 x 1080 1080P

#alexRegions
regions = {
    'player1rank': (125, 156, 22, 18)
    ,'player2rank': (1410, 158, 22, 18)
    ,'player1rank_vftv': (149, 165, 25, 18)
    ,'player2rank_vftv': (1382, 167, 23, 15)
    ,'player1_rounds': (519, 78, 106, 36)
    ,'player2_rounds': (840, 78, 106, 36)
    ,'stage': (619, 503, 240, 39)
    ,'player2ringname':  (1000, 535, 378, 35)
    ,'player1character': (54,    386,   418, 76)               
    ,'player2character': (1004,  386,    418, 76)
    ,'player1ringname':  (75, 540, 378, 28)        
    ,'vs': (586+12, 284+10, 308-45, 154-20)
    ,'ko': (438, 302, 627, 237)
    ,'excellent': (167, 341, 1146, 155)
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
    'player1rank': (72, 91, 14, 10)
    ,'player2rank': (820, 91, 14, 10)
    ,'player1_rounds': (519, 78, 106, 36)
    ,'player2_rounds': (840, 78, 106, 36)
    ,'stage': (619, 503, 240, 39)
    ,'player2ringname':  (1000, 535, 378, 35)
    ,'player1character': (54,    386,   418, 76)               
    ,'player2character': (1004,  386,    418, 76)
    ,'player1ringname':  (75, 540, 378, 28)        
    ,'vs': (586+12, 284+10, 308-45, 154-20)
    ,'ko': (438, 302, 627, 237)
    ,'excellent': (167, 341, 1146, 155)
}

regions_360p = {
    'player1rank': (53, 68, 13, 8)
    ,'player2rank': (614, 68, 13, 8)
    ,'player1_rounds': (519, 78, 106, 36)
    ,'player2_rounds': (840, 78, 106, 36)
    ,'stage': (619, 503, 240, 39)
    ,'player2ringname':  (1000, 535, 378, 35)
    ,'player1character': (54,    386,   418, 76)               
    ,'player2character': (1004,  386,    418, 76)
    ,'player1ringname':  (75, 540, 378, 28)        
    ,'vs': (586+12, 284+10, 308-45, 154-20)
    ,'ko': (438, 302, 627, 237)
    ,'excellent': (167, 341, 1146, 155)
}

# min width 25
def get_player_rank(player_num, frame, vftv=False, retry=0, override_regions=None):    
    if (retry > 5):
        return 0
    
    local_regions = None
    
    if (not override_regions is None):        
        local_regions = override_regions
    else:
        local_regions = regions

    (x, y, w, h) = local_regions[f"player{player_num}rank"]
    
    if (vftv and override_regions is None):
        (x, y, w, h) = local_regions[f"player{player_num}rank_vftv"]        

    #print(f"retry: {retry}")

    if (retry == 1):
        w = w -1
    elif (retry ==2):
        x = x - 29
        y = y - 10
    elif (retry ==3):
        x = x + 29
        y = y - 10
    elif (retry ==4):
        x = x - 20
        y = y - 10
    elif (retry ==5):
        x = x + 26
        y = y - 8

    roi = frame[y:y+h, x:x+w]                        

    #cv2.imshow("rank", roi  )
    #cv2.waitKey()
    
    all_white_roi = all_but_grey(roi)
    if (vftv):
        all_white_roi = all_but_white_vftv(roi)

    imagem = cv2.bitwise_not(all_white_roi)

    #cv2.rectangle(frame, (x, y), (x+w, y+h), color=(255,0,0), thickness=10)
    #cv2.imshow("rank", frame)    
    #cv2.waitKey()

    
    text = pytesseract.image_to_string(imagem, timeout=2, config="--psm 7")

    #text = str.replace(text, "\n\x0c", "")
    #text = str.replace(text, "\x0c", "")
    #text = str.replace(text, "?", "")
    #text = str.replace(text, "‘", "")

    text = re.sub("[^0-9]", "", text)

    #cv2.imshow("rank", roi)
    #print(text)
    #cv2.waitKey()

    if (not text.isnumeric()):
        return get_player_rank(player_num, frame, vftv, retry+1, override_regions);
    
    if (int(text) < 10):
        return 0
            
    greyCount = count_pixels("#7c7a82", roi)
    if (int(text) > 46 and retry < 3):
        return get_player_rank(player_num, frame, vftv, retry+1, override_regions)

    if (int(text) >= 40 and greyCount > 130):
        return (int(text)-10)

    if (int(text) < 0):
        return 0

    return int(text)        

def get_player_rank_black(player_num, frame, vftv=False):

    (x, y, w, h) = regions[f"player{player_num}rank"]
    if (vftv):
        (x, y, w, h) = regions[f"player{player_num}rank_vftv"]

    roi = frame[y:y+h, x:x+w]                        

    #cv2.imshow("rank", roi  )
    #cv2.waitKey()
    
    all_white_roi = all_but_grey(roi)
    if (vftv):
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

    cv2.imshow("rank", imagem)
    cv2.waitKey()
    print(text)

    return int(text)        

def load_sample_with_transparency(path):
    # Load the image with transparency
    sample_image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if sample_image is None:
        raise ValueError("Sample image not found")

    return sample_image

player1roundwon = load_sample_with_transparency('assets/player1roundwon.png')
player2roundwon = load_sample_with_transparency('assets/player2roundwon.png')


#min width = 50
def is_vs(frame, retry = 0, override_regions = None):
    if (retry == 3):
        return False
    
    (x, y, w, h) = regions["vs"]

    if (override_regions is not None):
        (x, y, w, h) = override_regions["vs"]

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
        
    roi = frame[y:y+h, x:x+w]

    all_white_roi = all_but_black_range(roi,
            np.array([0,0,0]),
            np.array([25,25,10])
            )

    if (override_regions == regions_1080p):
        all_white_roi = all_but_black_range(roi,
            np.array([0,0,0]),
            np.array([25,25,15])
            )

    #if (retry == 0):
        #all_white_roi = image_resize(all_white_roi, width=50)
        
    text = pytesseract.image_to_string(all_white_roi, config="--psm 7")

    #cv2.imshow('Video Frame', all_white_roi)            
    #cv2.waitKey()
    #print(text)

    text = text.strip()

    if (len(text) > 20):
        return False
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
    
    return is_vs(frame, retry+1)

def is_ko(roi):
    count = count_pixels('#ce9e54', roi)
    #print(f"is ko {count}")
    return count > 13600

def is_excellent(roi):
    count = count_pixels('#c48e36', roi)
    #print(f"is excellent {count}")
    return count > 14000

def is_ringout(roi):
    count = count_pixels('#07a319', roi)    
    return count > 8200

def extract_and_match_features(sample_image, frame_roi, feature_detector):

    #cv2.imshow('Video Frame', sample_image)
    #cv2.waitKey()

    #cv2.imshow('Video Frame', frame_roi)
    #cv2.waitKey()

    # Convert images to HSV
    sample_hsv = cv2.cvtColor(sample_image, cv2.COLOR_BGR2HSV)
    frame_hsv = cv2.cvtColor(frame_roi, cv2.COLOR_BGR2HSV)

    # Split into channels
    sample_h, sample_s, sample_v = cv2.split(sample_hsv)
    frame_h, frame_s, frame_v = cv2.split(frame_hsv)

    # Detect and compute keypoints and descriptors for each channel
    kp_sample_h, des_sample_h = feature_detector.detectAndCompute(sample_h, None)
    kp_frame_h, des_frame_h = feature_detector.detectAndCompute(frame_h, None)

    kp_sample_s, des_sample_s = feature_detector.detectAndCompute(sample_s, None)
    kp_frame_s, des_frame_s = feature_detector.detectAndCompute(frame_s, None)

    kp_sample_v, des_sample_v = feature_detector.detectAndCompute(sample_v, None)
    kp_frame_v, des_frame_v = feature_detector.detectAndCompute(frame_v, None)

    # BFMatcher to match descriptors
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)

    matches_h = bf.knnMatch(des_sample_h, des_frame_h, k=2)
    matches_s = bf.knnMatch(des_sample_s, des_frame_s, k=2)
    matches_v = bf.knnMatch(des_sample_v, des_frame_v, k=2)

    # Combine matches from all channels
    matches = matches_h + matches_s + matches_v
    matches = sorted(matches, key=lambda x: x.distance)

    return matches, kp_sample_h, kp_frame_h, frame_h

# Initialize the ORB detector
orb = cv2.ORB_create()

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

def count_pixels(target_color, image):
    tolerance = 40  # Adjust this value as needed

        # Convert the target color from hex to BGR
    target_color_bgr = tuple(int(target_color[i:i+2], 16) for i in (5, 3, 1))
    
    # Define the lower and upper bounds for the color
    lower_bound = np.array([max(c - tolerance, 0) for c in target_color_bgr], dtype=np.uint8)
    upper_bound = np.array([min(c + tolerance, 255) for c in target_color_bgr], dtype=np.uint8)
    
    # Create a mask that identifies all pixels within the color range
    mask = cv2.inRange(image, lower_bound, upper_bound)
    
    # Count the number of non-zero (white) pixels in the mask
    return cv2.countNonZero(mask)

    
def count_rounds_won(frame, playerNumber=1, vftv=False):

    region=regions[f"player{playerNumber}_rounds"]

    (x, y, w, h) = region        
    if (vftv):
        y+=10
        x+=10
        w-=10
        
    roi = frame[y:y+h, x:x+w]

    # Convert BGR to HSV
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)


    # Define range of red color in HSV
    if (playerNumber == 1):
        red_pixel_count = count_pixels("#e02958", roi)

        #print(red_pixel_count)
        #cv2.imshow("roi", roi)
        #cv2.waitKey()
                
        if (red_pixel_count > 700):
            return 3

        if (red_pixel_count > 380):
            return 2

        if (red_pixel_count >= 231):
            return 1    

    else:
        #ce9e54

        target_color = '#0d6ed7'  # Blue color
        count = count_pixels(target_color, roi)

        #print(count)
        #cv2.imshow("roi", roi)
        #cv2.waitKey()
        
        if (count > 305):
            return 3

        if (count > 200):
            return 2

        if (count > 100):
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

def all_but_white_vftv(roi):
    lower_white = np.array([100, 100, 100])  # Lower bound of white color
    upper_white = np.array([255, 255, 255])  # Upper bound of white color
    mask = cv2.inRange(roi, lower_white, upper_white)

    # Apply the mask to keep only white areas in the ROI
    white_only_roi = cv2.bitwise_and(roi, roi, mask=mask)            
    return white_only_roi

def get_ringname(player_num, frame):
    region_name=f"player{player_num}ringname"

    (x, y, w, h) = regions[region_name]
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
        
    if ("\"" in text):
        return None

    if ("\n" in text):
        return None
    
    if ("=" in text):
        return None
    
    if (len(text) >= 3):
        return text
    return None

# Min width of frame is 85
def get_stage(frame, override_region=None):
    region_name="stage"

    (x, y, w, h) = regions[region_name]
    if (override_region is not None):
        (x, y, w, h) = override_region[region_name]
        
    roi = frame[y:y+h, x:x+w]

    all_white_roi = all_but_grey(roi)
    #all_white_roi = image_resize(all_white_roi, width = 85)

    imagem = cv2.bitwise_not(all_white_roi)

    text = pytesseract.image_to_string(imagem, config="--psm 6", nice=-20)
    text = str.replace(text, "\n\x0c", "")        

    #cv2.imshow("roi", roi)    
    #print(text)
    #cv2.waitKey()

    if (text == "Water falls"):
        return "Waterfalls"
    
    if (text == "Ssfand"):
        return "Island"
    
    if (text == "Tampia"):
        return "Temple"
    
    if (text == "Island"):
        return "Island"
    
    if ("Arena" == text):
        return "Arena"
    
    if ("Palace" == text):
        return "Palace"

    if ("Aurora" == text):
        return "Aurora"
    
    if ("Temple" == text):
        return "Temple"
    
    if ("Sumo Ring" == text):
        return "Sumo Ring"
    
    if ("Ruins" == text):
        return "Ruins"
    
    if ("Statues" == text):
        return "Statues"

    if ("Great Wall" == text):
        return "Great Wall"

    if ("Wall" in text):
        return "Great Wall"

    if ("City" == text):
        return "City"
    
    if ("Terrace" == text):
        return "Terrace"
    
    if ("River" == text):
        return "River"

    if ("fall" in text):
        return "Waterfalls"

    if ("Water" in text):
        return "Waterfalls"

    if ("Waterfalls" in text):
        return "Waterfalls"
        
    if ("Grass" in text):
        return "Grassland"

    if ("Deep" in text):
        return "Deep Mountain"
    
    if ("Broken" in text or "House" in text):
        return "Broken House"
    
    if ("Genesis" == text):
        return "Genesis"
    
    if ("Shrine" == text):
        return "Shrine"

    if (text == "Training Room"):
        return "Training Room"

    if ("Snow" in text):
        return "Snow Mountain"        

    if ("Palace" in text):
        return "Palace"

    if ("Temple" in text):
        return "Temple"

    if ("Ruins" in text):
        return "Ruins"

    return None

def get_character_name(player_num, frame, retry=0):
    region_name = f"player{player_num}character"
    (x, y, w, h) = regions[region_name]
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
    #cv2.imshow("roi", roi)
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
        return get_character_name(player_num, frame, retry+1)
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