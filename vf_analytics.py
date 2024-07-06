import cv2
import numpy as np


vs_image = cv2.imread('vs.png')
vs_image_gray = cv2.cvtColor(vs_image, cv2.COLOR_BGR2GRAY)
vs_w, vs_h = vs_image_gray.shape[::-1]

def load_sample_with_transparency(path):
    # Load the image with transparency
    sample_image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if sample_image is None:
        raise ValueError("Sample image not found")

    # Check if the image has an alpha channel
    if sample_image.shape[2] == 4:
        print("got alpha channel")
        # Separate the color and alpha channels
        #bgr = sample_image[:, :, :3]
        #alpha = sample_image[:, :, 3]

        # Create a mask from the alpha channel
        #mask = alpha > 0

        # Create a new image with the transparent areas set to black
        #new_sample = np.zeros_like(bgr, dtype=np.uint8)
        #new_sample[mask] = bgr[mask]

        #return new_sample
    #else:
    return sample_image

player1roundwon = load_sample_with_transparency('player1roundwon.png')
player2roundwon = load_sample_with_transparency('player2roundwon.png')


def is_vs(roi):
    main_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(main_gray, vs_image_gray, cv2.TM_CCOEFF_NORMED)

    # Set a threshold for the match
    threshold = 0.8
    loc = np.where(result >= threshold)

    return (len(loc[0]) > 0)

def extract_and_match_features(sample_image, frame_roi, feature_detector):

    cv2.imshow('Video Frame', sample_image)
    cv2.waitKey()

    cv2.imshow('Video Frame', frame_roi)
    cv2.waitKey()

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

def count_rounds_won(frame, playerNumber=1):
    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    
    # Define range of red color in HSV
    if (playerNumber == 1):
        #resized = resize_sample_if_needed(player1roundwon, frame)

        #keypoints_sample, descriptors_sample = orb.detectAndCompute(resized, None)
        #matches, kp_sample, kp_frame, roi_h = extract_and_match_features(, frame, orb)
        #print (matches)

        lower_1 = np.array([0, 50, 50])      # Lower bound of red color in HSV
        upper_1 = np.array([10, 255, 255])   # Upper bound of red color in HSV

        lower_2 = np.array([170, 50, 50])    # Lower bound for the second range of red color
        upper_2 = np.array([180, 255, 255])  # Upper bound for the second range of red color

        # Create masks for red color
        mask1 = cv2.inRange(hsv, lower_1, upper_1)
        mask2 = cv2.inRange(hsv, lower_2, upper_2)


        # Combine masks to get the final red mask
        red_mask = mask1 | mask2

        # Count the number of red pixels
        red_pixel_count = np.sum(red_mask == 255)
        print(f"Number of red pixels: {red_pixel_count}")    

        if (red_pixel_count > 1200):
            return 3

        if (red_pixel_count > 1000):
            return 2

        if (red_pixel_count > 400):
            return 1    

    else:
        lower_1 = np.array([3, 41, 82])      # Lower bound of red color in HSV
        upper_1 = np.array([4, 42, 83])   # Upper bound of red color in HSV

        lower_2 = np.array([4,  42, 83])    # Lower bound for the second range of red color
        upper_2 = np.array([5,  43, 84])  # Upper bound for the second range of red color

        # Create masks for red color
        mask1 = cv2.inRange(hsv, lower_1, upper_1)
        mask2 = cv2.inRange(hsv, lower_2, upper_2)


        # Combine masks to get the final red mask
        red_mask = mask1 | mask2

        # Count the number of red pixels
        red_pixel_count = np.sum(red_mask == 255)
        print(f"Number of blue pixels: {red_pixel_count}")    

        if (red_pixel_count > 1200):
            return 3

        if (red_pixel_count > 1000):
            return 2

        if (red_pixel_count > 400):
            return 1
            
    return 0

def is_vf_character_name(name):
    if "Vanessa" in name:
        return True
    if "Blaze" in name:
        return True
    return False