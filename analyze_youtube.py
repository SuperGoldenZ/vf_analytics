import cv2
import pytesseract
from pytube import YouTube
import os.path
import numpy as np
from timeit import default_timer as timer
from threading import Thread
import vf_analytics
import vf_match
import uuid
import multiprocessing

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

def get_frame(video_path, count, frames):
    cap = cv2.VideoCapture(video_path )
    count = int(count)
    cap.set(cv2.CAP_PROP_POS_FRAMES, count)
    ret, frame = cap.read()
    if not ret:        
        return False
    
    frames[count] = frame
    #cv2.imshow('video frfame', frame)
    #cv2.waitKey()

    cap.release()
    
# Step 2: Extract frames from the video
def extract_frames(video_path, interval):
    get_available_devices()
    
    cap = cv2.VideoCapture(video_path )
    print(cap.getBackendName())

    frames = [None] * 500000
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    end_frame = None
    if end_frame is None or end_frame > frame_count:
        end_frame = frame_count
    cap.release()

    #22020
    #startFrame = 60 * 60 * 30
    startFrame=22020
    count = startFrame 

    caps = [None] * multiprocessing.cpu_count()
    
    while count < end_frame:
        #threads = [None] * multiprocessing.cpu_count()
        

        #threads = [None] * 1
        
        #for i in range(len(threads)):            

            #threads[i] = Thread(target=get_frame, args=[video_path+str(i), count, frames])
            #threads[i].start()
            #count+=(frame_rate*interval)
        
        #for i in range(len(threads)):
            #threads[i].join()

        get_frame(video_path, count, frames)
        print(count)
        count+=(frame_rate * interval)
        if (count > 57000):
            break    
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

def print_csv(match, round, round_num):
    print(match["id"], end = ",")
    print(match["stage"], end = ",")
    print(match["player1ringname"], end = ",")
    print(match["player1character"], end = ",")
    print(match["player2ringname"], end = ",")
    print(match["player2character"], end = ",")
    print(round_num, end = ",")
    print(round["player1_rounds"], end = ",")
    print(round["player1_ko"], end = ",")
    print(round["player1_ringout"], end = ",")
    print(round["player1_excellent"], end = ",")
    print(round["player2_rounds"], end = ',')
    print(round["player2_ko"], end = ",")
    print(round["player2_ringout"], end = ",")
    print(round["player2_excellent"])

def new_round():
    round = {}
    round["player1_excellent"] = 0
    round["player2_excellent"] = 0
    round["player1_ko"] = 0
    round["player2_ko"] = 0
    round["player1_ringout"] = 0
    round["player2_ringout"] = 0    
    round["player1_rounds"] = 0
    round["player2_rounds"] = 0
    return round

def get_character_name(region_name, match, frame):
    if (region_name in match):
        return
    (x, y, w, h) = vf_analytics.regions[region_name]
    roi = frame[y:y+h, x:x+w]                        
    
    white_only_roi = all_but_white(roi)
    text = pytesseract.image_to_string(white_only_roi)
    if (vf_analytics.is_vf_character_name(text)):
        text = str.replace(text, "\n\x0c", "")                
    if (text == "EI Blaze"):
        text = "El Blaze"
    if (text != ""):
        match[region_name] = text

def get_ringname(region_name, match, frame):
    if (region_name in match):
        return
    (x, y, w, h) = vf_analytics.regions[region_name]
    roi = frame[y:y+h, x:x+w]                        
    
    text = pytesseract.image_to_string(roi)
    text = str.replace(text, "\n\x0c", "")
    if (not " " in text):                    
        match[region_name] = text                

def get_stage(region_name, match, frame):
    if (region_name in match):
        return
    
    (x, y, w, h) = vf_analytics.regions[region_name]
    roi = frame[y:y+h, x:x+w]                        
    text = pytesseract.image_to_string(roi)
    text = str.replace(text, "\n\x0c", "")

    if (text != "" and not region_name in match):
        match[region_name] = text                

def got_all_vs_info(match):
    if (not "stage" in match):
        return False
    if (not "player1character" in match):
        return False
    if (not "player2character" in match):
        return False
    if (not "player1ringname" in match):
        return False
    if (not "player2ringname" in match):
        return False
            
    return True

def get_rounds_won(player_num, frame):
    (x, y, w, h) = vf_analytics.regions[f"player{player_num}_rounds"]
    roi = frame[y:y+h, x:x+w]                        
    return vf_analytics.count_rounds_won(roi, player_num)    

def process_excellent(player_num, frame, round):
    (x, y, w, h) = vf_analytics.regions['excellent']                    
    roi = frame[y:y+h, x:x+w]
    if (vf_analytics.is_excellent(roi)):
        round[f"player{player_num}_excellent"] = 1

def process_ko(player_num, frame, round):
    (x, y, w, h) = vf_analytics.regions['ko']                    
    roi = frame[y:y+h, x:x+w]
    if (vf_analytics.is_ko(roi)):
        round[f"player{player_num}_ko"] = 1

def process_ringout(player_num, frame, round):
    (x, y, w, h) = vf_analytics.regions['excellent']
    roi = frame[y:y+h, x:x+w]
    if (vf_analytics.is_ringout(roi)):
        round[f"player{player_num}_ringout"] = 1

# Step 3: Perform OCR on specific regions
def perform_ocr_on_frames(frames):
    results = []

    #height, width = list(frames.keys())[0].shape

    #height, width, _ = frames[0].shape  # Get the dimensions of the frame
    #print(f"{width} x {height}")

    #originalWidth=640
    #originalHeight=359

    
    state="before"    
    round=new_round()
    rounds_won=[0, 0]
    match={}
    round_num = 1

    match["id"] = uuid.uuid4()
    for frame in frames:        
        if frame is None:
            continue

        if (state == "before"):
            (x, y, w, h) = vf_analytics.regions["vs"]
            roi = frame[y:y+h, x:x+w]                        
            if (vf_analytics.is_vs(roi)):
                state="vs"                
                continue

        if (state == "vs"):                                                
            get_character_name("player1character", match, frame)
            get_character_name("player2character", match, frame)

            get_ringname("player1ringname", match, frame)
            get_ringname("player2ringname", match, frame)

            get_stage("stage", match, frame)
        
            if (got_all_vs_info(match)):
                state="fight"                
                continue
        
        if (state == "fight"):            
            #Check if match is over
            for player_num in range(1, 3):
                cnt=get_rounds_won(player_num, frame)
                
                if (cnt > 0 and cnt - rounds_won[player_num-1] == 1):
                    process_excellent(player_num, frame, round)
                    process_ko(player_num, frame, round)
                    process_ringout(player_num, frame, round)
                    round[f"player{player_num}_rounds"] = cnt
                    rounds_won[player_num-1]=cnt
                    
                    print_csv(match, round, round_num)
                    if (cnt < 3):
                        round=new_round()
                        round_num+=1

            if (round["player1_rounds"] == 3 or round["player2_rounds"] == 3):                                                                                                
                state="before"                
                round=new_round()
                rounds_won=[0, 0]
                round_num = 1
                match={}                                        
                match["id"] = uuid.uuid4()                

    return results

# Main function to run the whole process
def main():
    #video_url = 'https://www.youtube.com/watch?v=641FbPAGjto'
    video_path = '/home/alex/2024-04-20 14-29-03.mkv'
    #if not (os.path.isfile(video_path)):
        #download_video(video_url, video_path)
    print("Extracting frames")
    start = timer()
    frames = extract_frames(video_path, 1)  # Extract a frame every 7 seconds
    elapsed_time = timer() - start # in seconds
    print(f"{elapsed_time} seconds to read video ")
    
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