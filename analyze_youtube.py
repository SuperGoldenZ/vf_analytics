import cv2
import pytesseract
from pytube import YouTube
import os.path
import numpy as np
from timeit import default_timer as timer

import vf_analytics
import vf_match
import uuid

##todo: get player ranks

##todo: get knockout or ring out

##todo: check it's accurate - make sure red circle count is the same for two frames in a row? 
# (this is to handle in case of flash in when player gets a new red circle)

##todo: speed up especially the text recognition

# Step 1: Download the YouTube video
def download_video(url, output_path='video.mp4'):
    yt = YouTube(url)
    ys = yt.streams.filter(res='720p').first()
    ys.download(filename=output_path)
    print(f"Downloaded {url} to {output_path}")

def get_available_devices():
    index = 0
    arr = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            break
        else: 
            arr.append(index)
        cap.release()
        index += 1
    return arr

# Step 2: Extract frames from the video
def extract_frames(video_path, interval):
    get_available_devices()
    
    cap = cv2.VideoCapture(video_path )
    print(cap.getBackendName())

    frames = []
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    count = 0
    cap.set(cv2.CAP_PROP_POS_FRAMES, 35020)
    #count = 22020
    count = 35020
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        count += 1
        if count % (frame_rate * interval) == 0:
            frames.append(frame)
            #cv2.imshow('Video Frame', frame)
            #cv2.waitKey()
            #break
        #if (count > 35000):
            #break
    cap.release()
    return frames

def all_but_grey(roi):
    lower_white = np.array([175, 175, 175])  # Lower bound of white color
    upper_white = np.array([255, 255, 255])  # Upper bound of white color
    mask = cv2.inRange(roi, lower_white, upper_white)

    # Apply the mask to keep only white areas in the ROI
    white_only_roi = cv2.bitwise_and(roi, roi, mask=mask)            
    return white_only_roi

def all_but_white(roi):
    lower_white = np.array([235, 235, 235])  # Lower bound of white color
    upper_white = np.array([255, 255, 255])  # Upper bound of white color
    mask = cv2.inRange(roi, lower_white, upper_white)

    # Apply the mask to keep only white areas in the ROI
    white_only_roi = cv2.bitwise_and(roi, roi, mask=mask)            
    return white_only_roi

def all_but_black(roi):
    lower_black = np.array([0, 0, 0])  # Lower bound of white color
    upper_black = np.array([35, 35, 35])  # Upper bound of white color
    mask = cv2.inRange(roi, lower_black, upper_black)

    white_background = np.ones_like(roi) * 255
    masked_image = np.where(mask[:, :, None] == 255, roi, white_background)

    # Convert to grayscale
    gray = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)

    # Increase contrast and threshold the image to make text more distinct
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)

    # Optional: Apply morphological operations to fill in the text
    kernel = np.ones((5, 5), np.uint8)
    filled_text = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    # Optional: Remove small noise
    cleaned_text = cv2.medianBlur(filled_text, 3)    
    return cleaned_text

def print_csv(match, rounds):
    print(match["id"], end = ",")
    print(match["stage"], end = ",")
    print(match["player1ringname"], end = ",")
    print(match["player1character"], end = ",")
    print(match["player2ringname"], end = ",")
    print(match["player2character"], end = ",")
    print(rounds["player1rounds"], end = ",")
    print(rounds["player2rounds"])


# Step 3: Perform OCR on specific regions
def perform_ocr_on_frames(frames):
    results = []

    height, width, _ = frames[0].shape  # Get the dimensions of the frame
    print(f"{width} x {height}")

    originalWidth=640
    originalHeight=359

    p1NameX = 22 / originalWidth
    p1NameY = 134/originalHeight

    p2NameX = 365/originalWidth
    p2NameY = 134/originalHeight

    playerNameWidth = 136 / originalWidth
    playerNameHeight = 22 / originalHeight

    # Define the coordinates of the regions to perform OCR on (x, y, width, height)
    regions = {
        'player1character': (int(width * p1NameX), int(p1NameY * height), int(width * playerNameWidth), int(height * playerNameHeight)),
        'player2character': (int(width * p2NameX), int(p2NameY * height), int(width * playerNameWidth), int(height * playerNameHeight))
    }
    
    #alexRegions
    regions = {
        'player1rank': (435, 517, 25, 15)
        ,'player1rounds': (519, 78, 106, 36)
        ,'player2rounds': (845, 78, 106, 36)
        ,'stage': (578, 506, 312, 39)
        ,'player2ringname':  (1000, 535, 378, 35)
        ,'player1character': (54,    386,   418, 76)               
        ,'player2character': (1004,  386,    418, 76)
        ,'player1ringname':  (75, 540, 378, 28)        
        ,'vs': (586, 284, 308, 154)
    }

    state="before"
    rounds={}
    match={}
    match["id"] = uuid.uuid4()
    for frame in frames:        
        for region_name, (x, y, w, h) in regions.items():
            roi = frame[y:y+h, x:x+w]                        
            if (state=="fight" and (region_name == "player1rounds" or region_name == "player2rounds")):
                if (region_name == "player1rounds"):
                    cnt=vf_analytics.count_rounds_won(roi, 1)
                else:
                    cnt=vf_analytics.count_rounds_won(roi, 2)

                if (not region_name in rounds):                    
                    rounds[region_name] = 0
                elif (cnt > 0 and (cnt-rounds[region_name]) == 1):
                    rounds[region_name]=cnt
                    print_csv(match, rounds)
                if (rounds[region_name] == 3):                                        
                    return True
                    state="before"
                    rounds={}
                    match={}
                    print(f"done -> {state}")   
                    
                    continue
                #cv2.imshow('Video Frame', roi)        
                #cv2.waitKey()
            #if (state=="fight"):
                #continue

            #if (region_name == "player1rank" and not "player1rank" in match) :                
                #white_only_roi = all_but_grey(roi)
                #text = pytesseract.image_to_string(white_only_roi)
                #cv2.imshow('Video Frame', white_only_roi)        
                #cv2.waitKey()                        
            if (region_name == "vs" and vf_analytics.is_vs(roi)):
                state="vs"                
                continue
            
            if (state == "begin"):                
                continue
            
            # Get info from the VS scren
            if (state == "vs"):                                                
                #Ger
                if ("character" in region_name and not region_name in match):
                    white_only_roi = all_but_white(roi)
                    text = pytesseract.image_to_string(white_only_roi)
                    if (vf_analytics.is_vf_character_name(text)):
                        text = str.replace(text, "\n\x0c", "")                
                    if (text == "EI Blaze"):
                        text = "El Blaze"
                    if (text != ""):
                        match[region_name] = text                
                if ("ringname" in region_name and not region_name in match):
                    text = pytesseract.image_to_string(roi)
                    text = str.replace(text, "\n\x0c", "")
                    if (not " " in text):                    
                        match[region_name] = text                
                if ("stage" in region_name and not region_name in match):
                    text = pytesseract.image_to_string(roi)
                    text = str.replace(text, "\n\x0c", "")

                    if (text != "" and not region_name in match):
                        match[region_name] = text                
            
                if ("stage" in match and "player1character" in match and "player2character" in match and "player1ringname" in match and "player2ringname" in match):
                    state="fight"


    return results

# Main function to run the whole process
def main():
    #video_url = 'https://www.youtube.com/watch?v=641FbPAGjto'
    video_path = '/home/alex/2024-04-20 14-29-03.mkv'
    #if not (os.path.isfile(video_path)):
        #download_video(video_url, video_path)
    print("Extracting frames")
    frames = extract_frames(video_path, 1)  # Extract a frame every 7 seconds

    print("Extracting results")
    start = timer()
    results = perform_ocr_on_frames(frames)
    elapsed_time = timer() - start # in seconds
    print(f"{elapsed_time} seconds to run")

    #for i, result in enumerate(results):
        #print(f"Frame {i}:")
        #for region, text in result.items():
            #print(f"  {region}: {text}")
    
    # Clean up by removing the downloaded video file
    #os.remove(video_path)

if __name__ == '__main__':
    main()