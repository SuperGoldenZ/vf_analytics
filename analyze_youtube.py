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

#####todo: resize others to be width 1467x824
# for the VF part only

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

def get_frame(video_path, count, frames, resize=False):
    cap = cv2.VideoCapture(video_path )
    count = int(count)
    cap.set(cv2.CAP_PROP_POS_FRAMES, count)
    ret, frame = cap.read()

    if not ret:        
        return False

    if (resize):
        frame=image_resize(frame, width=1467)

    frames[count] = frame
    #cv2.imshow('video frfame', frame)
    #cv2.waitKey()

    cap.release()
    
# Step 2: Extract frames from the video
def extract_frames(video_path, interval):
    #get_available_devices()
    
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
    #startFrame = 60 * 60 * 28

    #pai start fraame
    #startFrame=60 * 60 * 24 + (16 * 60)

    #startFrame=22020

    #startFrame=60*60*11+(20*60)

    startFrame=1
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

        get_frame(video_path, count, frames, True)
        
        #cv2.imshow("v", frames[int(count)])
        #cv2.waitKey()
        
        print(count) 
        count+=(frame_rate * interval)
        #if (count > startFrame + 5000):
            #break    
    return frames

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
    f = open("match_data.csv", "a")    
    
    f.write(str(match["id"]))
    f.write(",")
    f.write(match["stage"])
    f.write(",")
    f.write(match["player1ringname"])
    f.write(",")
    f.write(str(match["player1rank"]))
    f.write(",")
    f.write(match["player1character"])
    f.write(",")
    f.write(match["player2ringname"])
    f.write(",")
    f.write(str(match["player2rank"]))
    f.write(",")
    f.write(match["player2character"])
    f.write(",")
    f.write(str(round_num))
    f.write(",")
    f.write(str(round["player1_rounds"]))
    f.write(",")
    f.write(str(round["player1_ko"]))
    f.write(",")
    f.write(str(round["player1_ringout"]))
    f.write(",")
    f.write(str(round["player1_excellent"]))
    f.write(",")
    f.write(str(round["player2_rounds"]))
    f.write(",")
    f.write(str(round["player2_ko"]))
    f.write(",")
    f.write(str(round["player2_ringout"]))
    f.write(",")
    f.write(str(round["player2_excellent"]))
    f.write("\n")
    f.close()

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
            if (vf_analytics.is_vs(frame)):
                state="vs"                                                

        if (state == "vs"):
            player1character = vf_analytics.get_character_name(1, frame)
            if (player1character is not None):
                match["player1character"] = player1character

            player2character = vf_analytics.get_character_name(2, frame)
            if (player2character is not None):
                match["player2character"] = player2character

            if (not "player1ringname" in match or match["player1ringname"] is None):
                player1ringname = vf_analytics.get_ringname(1, frame)                
                match["player1ringname"] = player1ringname
                    

            if (not "player2ringname" in match or match["player2ringname"] is None):
                player2ringname = vf_analytics.get_ringname(2, frame)                
                match["player2ringname"] = player2ringname

            if ("stage" not in match):
                stage=vf_analytics.get_stage(frame)
                if (stage is not None):
                    match["stage"] = stage
                                
            if (got_all_vs_info(match)):
                state="fight"                
                continue
        
        if (state == "fight"):            
            if (not "player1rank" in match or match["player1rank"] == 0):
                try:
                    match["player1rank"] = vf_analytics.get_player_rank(1, frame, True)
                except:
                    match["player1rank"] = 0

            if (not "player2rank" in match or match["player2rank"] == 0):
                try:
                    match["player2rank"] = vf_analytics.get_player_rank(2, frame, True)
                except:
                    match["player2rank"] = 0


            #Check if match is over
            for player_num in range(1, 3):
                cnt=get_rounds_won(player_num, frame)

                process_excellent(player_num-1, frame, round)
                process_ko(player_num-1, frame, round)
                process_ringout(player_num-1, frame, round)
                                    
                if (cnt > 0 and cnt - rounds_won[player_num-1] == 1):
                    round[f"player{player_num}_rounds"] = cnt
                    rounds_won[player_num-1]=cnt
                    print_csv(match, round, round_num)
                    if (cnt < 3):
                        round=new_round()
                        round["player1_rounds"]=rounds_won[0]
                        round["player2_rounds"]=rounds_won[1]
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
    
    video_path = '/home/alex/vf_analytics/blaze01.mp4'
    video_url = 'https://www.youtube.com/watch?v=ukTR1jyBC1Y'
    if not (os.path.isfile(video_path)):
        download_video(video_url, video_path)


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