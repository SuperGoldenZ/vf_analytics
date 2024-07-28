import cv2
import os.path
import numpy as np
from timeit import default_timer as timer
from threading import Thread
import vf_analytics
import youtube_helper
import uuid
import sys
import psutil
import logging
import argparse
import pathlib
import ffmpeg
import time

logger = None
resize_video = False
youtube_auth = True
force_append=False

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

def save_cam_frame(jpg_folder, original_frame, frame, count_int, suffix):
    hdd = psutil.disk_usage('/')

    if not os.path.exists(jpg_folder + "/original/"):
        os.makedirs(jpg_folder + "/original/")

    out_filename = jpg_folder + "/original/" + str(f"{count_int}_{suffix}") + ".png"
    try:
        if (jpg_folder is not None and hdd.free > 10567308288):
            cv2.imwrite(out_filename, original_frame)
    except Exception as e:
        logger.error(f"Error write to image file {out_filename}")
        logger.error(repr(e))

    out_filename = jpg_folder + "/" + str(f"{count_int}_{suffix}") + ".png"
    try:
        if (jpg_folder is not None and hdd.free > 10567308288):
            cv2.imwrite(out_filename, frame)
    except Exception as e:
        logger.error(f"Error write to image file {out_filename}")
        logger.error(repr(e))
        
    
# Step 2: Extract frames from the video
def extract_frames(video_path, interval, video_folder=None, video_id="n/a", jpg_folder="jpg", regions=None, cam=-1):
    cap = None
    if (video_path is not None):
        cap = cv2.VideoCapture(video_path )
    else:
        cap = cv2.VideoCapture(cam)
        cap.set( cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set( cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        if not cap.isOpened():
            print (f"Failed to open CAM {cam}")
            return

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

    if (cam != -1):
        jpg_folder = "assets/jpg/cam"
        if not os.path.exists(jpg_folder):
            os.makedirs(jpg_folder)

    while count < end_frame or cam != -1:
        count_int = int(count)

        #use epoch time for cam
        if (cam != -1):
            count_int = int(time.time() * 1000)
            count = count_int

        frame = None
        if (skipFrames > 0):
            skipFrames-=1
            count+=int(frame_rate * interval)
            logger.debug(f"skipping frames {skipFrames} left")
            print(f"{video_id} {count_int} skipping frames {skipFrames} left")
            if (cam != -1):
                cap.read()
                time.sleep(interval)                
            continue

        original_frame = None

        if (cam == -1 and os.path.isfile(jpg_folder + "/" + str(f"{count_int:13d}") + ".jpg")):
            try:
                filename = jpg_folder + "/" + str(f"{count_int:13d}") + ".jpg"
                frame = cv2.imread(filename)
            except Exception as e:
                logger.error(f"{video_id} {count:13d} [ERROR] - error reading from image file", file=sys.stderr)
                logger.error(repr(e))
                continue
        else:
            if (cam == -1):
                cap.set(cv2.CAP_PROP_POS_FRAMES, count)

            ret, frame = cap.read()
            if not ret:
                print("could not read frame")
                logger.warn(f"Skipping frame {count:13d} because no return")
                continue

            if (cam == -1):
                frame = vf_analytics.remove_black_border(frame, resize_height=480)
            else:
                vf_analytics.resolution="480p"

        if frame is None:
            continue

        original_frame = frame
        frame = cv2.resize(frame, (854, 480))

        if (state == "before"):
            logger.debug(f"BEFORE - searching for vs frame count {count}")
            print(f"BEFORE - searching for vs frame count {count}")
            #if (vf_analytics.is_vs(frame)):
            stage=vf_analytics.get_stage(frame)
            if (stage is not None):
                match["stage"] = stage
                state="vs"
                logger.debug(f"{video_id} {count:13d} - got stage {stage} and setting to vs")

                if (cam == -1):
                    print(f"{video_id} {count:13d} - got stage {stage} and setting to vs")
                else:
                    print(f"camera: {cam} {count:13d} - got stage {stage} and setting to vs")

                

        if (state == "vs"):
            if (match.get('player1character') is None):
                player1character = vf_analytics.get_character_name(1, frame)
                if (player1character is not None):
                    match["player1character"] = player1character
                    logger.debug(f"{video_id} {count:13d} - player 1 character {player1character}")

            if (match.get('player2character') is None):
                player2character = vf_analytics.get_character_name(2, frame)
                if (player2character is not None):
                    match["player2character"] = player2character
                    logger.debug(f"{video_id} {count:13d} - player 2 character {player2character}")

            if (not "player1ringname" in match or match["player1ringname"] is None):
                player1ringname = vf_analytics.get_ringname(1, frame)
                match["player1ringname"] = player1ringname
                logger.debug(f"{video_id} {count:13d} - player 1 is {player1ringname}")

            if (not "player2ringname" in match or match["player2ringname"] is None):
                player2ringname = vf_analytics.get_ringname(2, frame)
                match["player2ringname"] = player2ringname
                logger.debug(f"{video_id} {count:13d} - player 2 is {player2ringname}")

            if ("stage" not in match):
                logger.debug(f"{video_id} {count:13d} - looking for stage")
                stage=vf_analytics.get_stage(frame)
                if (stage is not None):
                    match["stage"] = stage
                    logger.debug(f"{video_id} {count:13d} - stage {stage}")

            if (got_all_vs_info(match)):
                state="fight"
                logger.debug(f"{video_id} {count:13d} - fight")
                print_csv(match, round, "0", video_id, count)
                
                skipFrames=(int) (40/interval)
                #skipFrames for 1
                #skipFrames=28
                print(f"got all match info: {count:13d} - fight")
                
                save_cam_frame(jpg_folder, original_frame, frame, count, "start")
                continue

        if (state == "fight"):
            if (not "player1rank" in match or match["player1rank"] == 0):
                try:
                    player1rank = vf_analytics.get_player_rank(1, frame, True)
                    match["player1rank"] = player1rank
                    logger.debug(f"{video_id} {count:13d} - player1rank {player1rank}")
                except:
                    match["player1rank"] = 0

            if (not "player2rank" in match or match["player2rank"] == 0):
                try:
                    player2rank = vf_analytics.get_player_rank(2, frame, True)
                    match["player2rank"] = player2rank
                    logger.debug(f"{video_id} {count:13d} - player2rank {player2rank}")
                except:
                    match["player2rank"] = 0
            
            player_num = vf_analytics.is_winning_round(frame)
            if (player_num == 0 ):
                save_cam_frame(jpg_folder, original_frame, frame, count, "notwin")
                logger.debug(f"{count_int} is not a winning round so continue")
                count+=int(frame_rate * interval)
                continue
            
            logger.debug(f"{video_id} {count:013d} - player {player_num} won the match")
                                    
            is_excellent = vf_analytics.is_excellent(frame)
            is_ko = not is_excellent and vf_analytics.is_ko(frame)
            is_ro = not is_excellent and not is_ko and vf_analytics.is_ringout(frame)

            if (is_excellent):
                round[f"player{player_num}_excellent"] = 1
                print(f"{count} got excellent for player {player_num}")
            elif (is_ko):
                round[f"player{player_num}_ko"] = 1
                print(f"{count} got KO player {player_num}")
            elif (is_ro):
                round[f"player{player_num}_ringout"] = 1
                print(f"{count} got ringout player {player_num}")
            else:
                print(f"{count} unknown way to victory for {player_num} skipping")
                count+=int(frame_rate * interval)

                thread = Thread(target=save_cam_frame,args=[jpg_folder, original_frame, frame, count, "unknown_skip"])
                thread.start()
    
                save_cam_frame(jpg_folder, original_frame, frame, count, "unknown_skip")
                continue

            rounds_won[player_num-1] = rounds_won[player_num-1] + 1
            round[f"player{player_num}_rounds"] = round[f"player{player_num}_rounds"] + 1
            
            try:
                print_csv(match, round, round_num, video_id, count)

                if (cam != -1):
                    suffix=""
                    if (is_excellent):
                        suffix=f"excellent_for_player{player_num}"
                    elif (is_ro):
                        suffix=f"ringout_for_player{player_num}"
                    elif (is_ko):
                        suffix=f"knockout_for_player{player_num}"
                    else:
                        suffix=f"unknownwin_for_player{player_num}"

                save_cam_frame(jpg_folder, original_frame, frame, count, suffix)
            except:
                logger.error(f"{video_id} {count:13d} ERROR write to csv")
            logger.debug(f"{video_id} {count:13d} - round {round_num} finished player {player_num} won")

            if (match["player1rank"] == 0):
                logger.error(f"{video_id} {count:13d} - round is over but player 1 rank is 0")
            if (match["player2rank"] == 0):
                logger.error(f"{video_id} {count:13d} - round is over but player 2 rank is 0")

            if (round[f"player{player_num}_rounds"] < 3):
                round=new_round()
                round["player1_rounds"]=rounds_won[0]
                round["player2_rounds"]=rounds_won[1]
                round_num+=1
                skipFrames = 10

                if (cam != -1):
                    skipFrames = 17

                print(f"{count} new round")
            else:         
                state="before"
                round=new_round()
                rounds_won=[0, 0]
                round_num = 1
                match={}
                match["id"] = uuid.uuid4()
                logger.debug(f"{video_id} {count:13d} - match finished")
                skipFrames=2

        #if (cam != -1):
            #time.sleep(0.25)

        if (state == "before"):
            count+=int(frame_rate * interval*4)
        else:
            count+=int(frame_rate * interval)

    if (state != "before"):
        logger.error(f"{video_id} {count:13d} - premature match aborted")
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

def print_csv(match, round, round_num, video_id, frame_count):
    f = open("match_data.csv", "a")

    if (video_id is None):
        f.write("cam")
    else:
        f.write(video_id)

    f.write(",")
    f.write(str(frame_count))
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
    try:
        f.write(str(match["player1rank"]))
    except:
        f.write("0")
    f.write(",")
    f.write(match["player1character"])
    f.write(",")
    f.write(match["player2ringname"])
    f.write(",")
    try:
        f.write(str(match["player2rank"]))
    except:
        f.write("0")
    f.write(",")
    f.write(match["player2character"])
    f.write(",")
    f.write(str(round_num))
    f.write(",")
    try:
        f.write(str(round["player1_rounds"]))
    except:
        f.write("0")
    f.write(",")
    try:
        f.write(str(round["player1_ko"]))
    except:
        f.write("0")
    f.write(",")

    try:
        f.write(str(round["player1_ringout"]))
    except:
        f.write("0")

    f.write(",")
    try:
        f.write(str(round["player1_excellent"]))
    except:
        f.write("0")

    f.write(",")
    try:
        f.write(str(round["player2_rounds"]))
    except:
        f.write("0")
    f.write(",")
    try:
        f.write(str(round["player2_ko"]))
    except:
        f.write("0")
    f.write(",")

    try:
        f.write(str(round["player2_ringout"]))
    except:
        f.write("0")
    f.write(",")

    try:
        f.write(str(round["player2_excellent"]))
    except:
        f.write("0")

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

# Step 3: Perform OCR on specific regions
def perform_ocr_on_frames(frames, video_id="n/a"):
    #height, width = list(frames.keys())[0].shape

    #height, width, _ = frames[0].shape  # Get the dimensions of the frame
    #print(f"{width} x {height}")

    #originalWidth=640
    #originalHeight=359


    return

def analyze_video(url, cam=-1):
    p = pathlib.Path('match_data.csv')
    if (not p.is_file()):
        with open('match_data.csv', 'a') as the_file:
            the_file.write('vid,match_id,stage,player1ringname,player1rank,player1character,player2ringname,player2rank,player2character,round_num,player1_rounds_won,p1ko,p1ro,p1ex,player2_rounds_won,p2ko,p2ro,p2ex\n')

    video_id=None
    video_folder=None
    video_path = None
    jpg_folder=None


    if (url is not None):
        video_id = youtube_helper.get_youtube_video_id(url)
        with open('match_data.csv') as f:
            if video_id in f.read() and force_append==False:
                print(f"Skipping {video_id} since it's already in match data")
                return

        ys = youtube_helper.get_stream(url)
        resolution = ys.resolution
        vf_analytics.resolution = resolution

        jpg_folder=f"assets/jpg/{video_id}_{resolution}"
        if not os.path.exists(jpg_folder):
            os.makedirs(jpg_folder)

        video_folder=f"assets/videos/{video_id}_{resolution}/"
        video_path  =f"assets/videos/{video_id}_{resolution}/video.mp4"

        if not os.path.exists(video_folder):
            os.makedirs(video_folder)

        if (not os.path.isfile(video_path)):
            try:
                logger.debug(f"Downloading video {url} at {resolution}")
                temp_path = youtube_helper.download_video(ys, video_id, resolution=resolution)

                print(f"Renaming video after download: {temp_path} to {video_path}")
                if (resolution != '480p' and resize_video):
                    ffmpeg.input(temp_path).output(video_path, vf='scale=854:480').run()
                    os.remove(temp_path)
                else:
                    os.rename(temp_path, video_path)
            except Exception as e:
                print(f"error downloading \"{url}\" ")
                print(ys)
                print(repr(e))
                return None
        else:
            print(f"Not downloading because exists: {video_path}")

    print("Extracting frames")
    start = timer()

    vf_analytics.resolution = "480p"
    resolution = "480p"

    fps=0.1
    extract_frames(video_path, fps, video_folder, video_id, jpg_folder, cam=cam)  # Extract a frame every 7 seconds


    start = timer()

    elapsed_time = timer() - start # in seconds
    print(f"{elapsed_time} seconds to run")

def process_playlist(playlist):
    urls = youtube_helper.get_video_urls_from_playlist(playlist)
    for url in urls:
        analyze_video(url)

def process_videos_list(urls):
    for url in urls:
        analyze_video(url)


def process_playlists(playlist_array):
    for playlist in playlist_array:
        process_playlist(playlist)

# Main function to run the whole process
def main(video_url = None, playlists_file=None, playlist_file=None, cam=-1):

    if (video_url is not None and "list=" in video_url):
        process_playlist(video_url)
        return

    if (video_url is not None):
        analyze_video(video_url)
        return

    if (cam != -1):
        analyze_video(cam=cam, url=None)
        return

    if (playlists_file is not None):
        playlists = []
        with open(playlists_file) as my_file:
            for line in my_file:
                if (line is not None):
                    line = line.strip()
                    playlists.append(line)
        process_playlists(playlists)
        return

    if (playlist_file is not None):
        videos = []
        with open(playlist_file) as my_file:
            for line in my_file:
                if (line is not None):
                    line = line.strip()
                    videos.append(line)
        process_videos_list(videos)
        return

    threads = []
    thread = Thread(target=process_playlists,args=[youtube_helper.play_collection])
    thread.start()
    threads.append(thread)

    thread = Thread(target=process_playlists,args=[youtube_helper.playlists])
    thread.start()
    threads.append(thread)

    print("going to join threads")
    threads[0].join()
    threads[1].join()

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='vf_match_analyzer.log', encoding='utf-8', level=logging.DEBUG)

    parser=argparse.ArgumentParser(description="Download and extract match data from VF5ES videos")
    parser.add_argument('--youtube-auth', default=True)
    parser.add_argument('--video_url', default=None, help="URL for youtube video or playlist to process")
    parser.add_argument('--playlists_file', default=None, help="Local file with list of playlists to process")
    parser.add_argument('--playlist_file', default=None, help="Local file with list of YouTube videos to process")
    parser.add_argument('--force_append', default=None, help="Force overwrite videos")
    parser.add_argument('--cam', default=None, help="Set to capture from camera")
    #parser.add_argument('--resolution', default='1080p', help="video resolution 10809p, 480p, 360p")

    args = parser.parse_args()

    video_url = None
    try:
        video_url=vars(args)['video_url']
        if (video_url is not None):
            video_url = video_url.strip()
    except:
        video_url=None

    playlists_file=None
    try:
        playlists_file=vars(args)['playlists_file']
        if (playlists_file is not None):
            playlists_file = playlists_file.strip()
    except:
        playlists_file=None

    playlist_file=None
    try:
        playlist_file=vars(args)['playlist_file']
        if (playlist_file is not None):
            playlist_file = playlist_file.strip()
    except:
        playlist_file=None

    try:
        fa=vars(args)['force_append']
        if (fa is not None):
            force_append=True
    except:
        force_append=False

    cam=None
    try:
        cam=vars(args)['cam']
        if (cam is not None):
            cam = cam.strip()
    except:
        cam=None

    #main(video_url)
    cam_int = -1
    if (cam is not None):
        cam_int = int(cam)

    #main(video_url)
    main(video_url=video_url, playlists_file=playlists_file, playlist_file=playlist_file, cam=cam_int)