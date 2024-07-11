import cv2
import os.path
import numpy as np
from timeit import default_timer as timer
from threading import Thread
import vf_analytics
import youtube_helper
import time
import uuid
import multiprocessing
import sys
import psutil
import pickle


#65661

#####todo: resize others to be width 1467x824
# for the VF part only

##todo: get player ranks

##todo: get knockout or ring out

##todo: check it's accurate - make sure red circle count is the same for two frames in a row? 
# (this is to handle in case of flash in when player gets a new red circle)

##todo: speed up especially the text recognition


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
    
# Step 2: Extract frames from the video
def extract_frames(video_path, interval, video_folder=None, video_id="n/a", jpg_folder="jpg"):    
    cap = cv2.VideoCapture(video_path )
                    
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    end_frame = None
    if end_frame is None or end_frame > frame_count:
        end_frame = frame_count
    

    startFrame=1
    count = startFrame 

    state="before"    
    round=new_round()
    rounds_won=[0, 0]
    match={}
    round_num = 1

    match["id"] = uuid.uuid4()
    
    skipFrames = 0
    hdd = psutil.disk_usage('/')

    while count < end_frame:        
        count_int = int(count)
        frame = None
        if (skipFrames > 0):
            skipFrames-=1
            count+=(frame_rate * interval)            
            continue

        if (os.path.isfile(jpg_folder + "/" + str(f"{count_int:06}") + ".jpg")):
            try:
                frame = cv2.imread(jpg_folder + "/" + str(f"{count_int:06}") + ".jpg")
            except:
                print(f"{video_id} {count:06} [ERROR] - error reading from image file", file=sys.stderr)
                continue
        else:
            cap.set(cv2.CAP_PROP_POS_FRAMES, count)
            ret, frame = cap.read()
            resize = True
            if not ret:
                continue
            if (resize):
                frame=image_resize(frame, width=1467)
            
            out_filename = jpg_folder + "/" + str(f"{count_int:06}") + ".jpg"
            try:
                if (jpg_folder is not None and hdd.free > 10567308288):                                
                    cv2.imwrite(out_filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 82])
            except Exception as e:
                print(f"{video_id} {count:06} [ERROR] - error write to image file {out_filename}", file=sys.stderr)
                print(repr(e))
            
        if frame is None:
            continue

        if (state == "before"):
            if (vf_analytics.is_vs(frame)):
                state="vs"
                print(f"{video_id} {count:06} - vs")

        if (state == "vs"):
            if (match.get('player1character') is None):
                player1character = vf_analytics.get_character_name(1, frame)
                if (player1character is not None):
                    match["player1character"] = player1character
                    print(f"{video_id} {count:06} - player 1 character {player1character}")

            if (match.get('player2character') is None):
                player2character = vf_analytics.get_character_name(2, frame)
                if (player2character is not None):
                    match["player2character"] = player2character
                    print(f"{video_id} {count:06} - player 2 character {player2character}")

            if (not "player1ringname" in match or match["player1ringname"] is None):
                player1ringname = vf_analytics.get_ringname(1, frame)                
                match["player1ringname"] = player1ringname
                print(f"{video_id} {count:06} - player 1 is {player1ringname}")                

            if (not "player2ringname" in match or match["player2ringname"] is None):
                player2ringname = vf_analytics.get_ringname(2, frame)                
                match["player2ringname"] = player2ringname
                print(f"{video_id} {count:06} - player 2 is {player2ringname}")

            if ("stage" not in match):
                stage=vf_analytics.get_stage(frame)
                if (stage is not None):
                    match["stage"] = stage
                    print(f"{video_id} {count:06} - stage {stage}")

            if (got_all_vs_info(match)):
                state="fight"                
                print(f"{video_id} {count:06} - fight")
                skipFrames=20
                continue
        
        if (state == "fight"):            
            if (not "player1rank" in match or match["player1rank"] == 0):
                try:
                    player1rank = vf_analytics.get_player_rank(1, frame, True)
                    match["player1rank"] = player1rank                                                                        
                    print(f"{video_id} {count:06} - player1rank {player1rank}")
                except:
                    match["player1rank"] = 0

            if (not "player2rank" in match or match["player2rank"] == 0):
                try:
                    player2rank = vf_analytics.get_player_rank(2, frame, True)
                    match["player2rank"] = player2rank
                    print(f"{video_id} {count:06} - player2rank {player2rank}")
                except:
                    match["player2rank"] = 0


            #Check if match is over
            for player_num in range(1, 3):
                cnt=vf_analytics.count_rounds_won(frame, player_num, True)

                process_excellent(player_num-1, frame, round)
                process_ko(player_num-1, frame, round)
                process_ringout(player_num-1, frame, round)
                                    
                if (cnt > 0 and cnt - rounds_won[player_num-1] == 1):
                    round[f"player{player_num}_rounds"] = cnt
                    rounds_won[player_num-1]=cnt
                    try:
                        print_csv(match, round, round_num, video_id)
                    except:
                        print(f"{video_id} {count:06} ERROR write to csv")
                    print(f"{video_id} {count:06} - round {round_num} finished player {player_num} won")
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
                print(f"{video_id} {count:06} - match finished")
                skipFrames=5


        count+=(frame_rate * interval)

    if (state != "before"):
        print(f"{video_id} {count:06} [ERROR] - premature match aborted", file=sys.stderr)
    hdd = psutil.disk_usage('/')

    if (hdd.free < 10567308288):
        os.remove(video_path)
    
    cap.release()
    return

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

def print_csv(match, round, round_num, video_id):
    f = open("match_data.csv", "a")    
        
    f.write(video_id)
    f.write(",")
    f.write(str(match["id"]))
    f.write(",")
    if (not "stage" in match or match["stage"] is None):
        f.write("n/a")
    else:
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
def perform_ocr_on_frames(frames, video_id="n/a"):    
    #height, width = list(frames.keys())[0].shape

    #height, width, _ = frames[0].shape  # Get the dimensions of the frame
    #print(f"{width} x {height}")

    #originalWidth=640
    #originalHeight=359

    
    return

def analyze_video(url):
    video_id = youtube_helper.get_youtube_video_id(url)    
    with open('match_data.csv') as f:
        if video_id in f.read():
            print(f"Skipping {video_id} since it's already in match data")
            return

    video_folder=f"/home/alex/vf_analytics/assets/videos/{video_id}"        
    if not os.path.exists(video_folder):
        os.makedirs(video_folder)
    video_path = video_folder + "/video.mp4"

    jpg_folder=f"/home/alex/vf_analytics/assets/jpg/{video_id}"
    if not os.path.exists(jpg_folder):
        os.makedirs(jpg_folder)
    
    if (not os.path.isfile(video_path)):        
        try:                
            print(f"Downloading video because not exists: {video_path}")
            youtube_helper.download_video(url, video_path)                        
        except Exception as e:
            print(f"error downloading {url}")                    
            print(repr(e))
            return None
    else:
        print(f"Not downloading because exists: {video_path}")

    print("Extracting frames")
    start = timer()
    

    extract_frames(video_path, 1, video_folder, video_id, jpg_folder)  # Extract a frame every 7 seconds
    
    
    start = timer()
    
    elapsed_time = timer() - start # in seconds
    print(f"{elapsed_time} seconds to run")
    
# Main function to run the whole process
def main():
    for playlist in youtube_helper.playlists:
        urls = youtube_helper.get_video_urls_from_playlist(playlist)

        num_cores = 2
        print(f"Number of available CPU cores: {num_cores}")
        
        threads = []
    
        for url in urls:
            if len(threads) >= num_cores:
                # Wait for the first thread in the list to finish if we reached the max number of threads
                threads[0].join()
                threads.pop(0)
            
            thread = Thread(target=analyze_video,args=[url])
            thread.start()
            threads.append(thread)            
                
if __name__ == '__main__':
    main()