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

logger = None
resize_video = False
youtube_auth = True

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
def extract_frames(video_path, interval, video_folder=None, video_id="n/a", jpg_folder="jpg", regions=None):
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
            count+=int(frame_rate * interval)
            logger.debug(f"skipping frames {skipFrames} left")
            continue

        if (os.path.isfile(jpg_folder + "/" + str(f"{count_int:06}") + ".jpg")):
            try:
                filename = jpg_folder + "/" + str(f"{count_int:06}") + ".jpg"
                frame = cv2.imread(filename)
                #logger.debug(f"loaded {filename} from local file")
            except:
                logger.error(f"{video_id} {count:10d} [ERROR] - error reading from image file", file=sys.stderr)
                continue
        else:
            cap.set(cv2.CAP_PROP_POS_FRAMES, count)
            ret, frame = cap.read()

            if not ret:
                logger.warn(f"Skipping frame {count:10d} because no return")
                continue

            out_filename = jpg_folder + "/" + str(f"{count_int:06}") + ".jpg"
            try:
                if (jpg_folder is not None and hdd.free > 10567308288):
                    cv2.imwrite(out_filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 100])
            except Exception as e:
                logger.error(f"{video_id} {count:10d} [ERROR] - error write to image file {out_filename}", file=sys.stderr)
                logger.error(repr(e))

        if frame is None:
            continue

        height, width, channels = frame.shape
        if (height != 480):
            frame = cv2.resize(frame, (854, 480))
        frame = vf_analytics.remove_black_border(frame)

        if (state == "before"):
            logger.debug(f"BEFORE - searching for vs frame count {count}")
            #if (vf_analytics.is_vs(frame)):
            stage=vf_analytics.get_stage(frame)
            if (stage is not None):
                match["stage"] = stage
                state="vs"
                logger.debug(f"{video_id} {count:10d} - got stage {stage}")
            logger.debug(f"{video_id} {count:10d} - vs")

        if (state == "vs"):
            if (match.get('player1character') is None):
                player1character = vf_analytics.get_character_name(1, frame)
                if (player1character is not None):
                    match["player1character"] = player1character
                    logger.debug(f"{video_id} {count:10d} - player 1 character {player1character}")

            if (match.get('player2character') is None):
                player2character = vf_analytics.get_character_name(2, frame)
                if (player2character is not None):
                    match["player2character"] = player2character
                    logger.debug(f"{video_id} {count:10d} - player 2 character {player2character}")

            if (not "player1ringname" in match or match["player1ringname"] is None):
                player1ringname = vf_analytics.get_ringname(1, frame)
                match["player1ringname"] = player1ringname
                logger.debug(f"{video_id} {count:10d} - player 1 is {player1ringname}")

            if (not "player2ringname" in match or match["player2ringname"] is None):
                player2ringname = vf_analytics.get_ringname(2, frame)
                match["player2ringname"] = player2ringname
                logger.debug(f"{video_id} {count:10d} - player 2 is {player2ringname}")

            if ("stage" not in match):
                logger.debug(f"{video_id} {count:10d} - looking for stage")
                stage=vf_analytics.get_stage(frame)
                if (stage is not None):
                    match["stage"] = stage
                    logger.debug(f"{video_id} {count:10d} - stage {stage}")

            if (got_all_vs_info(match)):
                state="fight"
                logger.debug(f"{video_id} {count:10d} - fight")
                skipFrames=22
                continue

        if (state == "fight"):
            if (not "player1rank" in match or match["player1rank"] == 0):
                try:
                    player1rank = vf_analytics.get_player_rank(1, frame, True)
                    match["player1rank"] = player1rank
                    logger.debug(f"{video_id} {count:10d} - player1rank {player1rank}")
                except:
                    match["player1rank"] = 0

            if (not "player2rank" in match or match["player2rank"] == 0):
                try:
                    player2rank = vf_analytics.get_player_rank(2, frame, True)
                    match["player2rank"] = player2rank
                    logger.debug(f"{video_id} {count:10d} - player2rank {player2rank}")
                except:
                    match["player2rank"] = 0


            #Check if match is over
            for player_num in range(1, 3):
                wonSoFar=rounds_won[player_num-1]
                try:
                    logger.debug(f"{video_id} {count:010d} - counting rounds won for player {player_num}")
                    cnt=vf_analytics.count_rounds_won(frame, player_num, wonSoFar=wonSoFar)
                except:
                    logger.warning(f"{video_id} {count:10d} ^^^^^^^^^^^^^^^^ skipping round won for player {player_num}")
                    continue

                if (cnt > 0 and cnt - wonSoFar == 1):
                    logger.debug(f"\tplayer {player_num} won the round cnt {cnt} sofar {wonSoFar}")
                    process_excellent(player_num, frame, round)
                    process_ko(player_num, frame, round)
                    process_ringout(player_num, frame, round)

                    #cv2.imshow("winning blow", frame)
                    #cv2.waitKey()

                    round[f"player{player_num}_rounds"] = cnt
                    rounds_won[player_num-1]=cnt
                    try:
                        print_csv(match, round, round_num, video_id)
                    except:
                        logger.error(f"{video_id} {count:10d} ERROR write to csv")
                    logger.debug(f"{video_id} {count:10d} - round {round_num} finished player {player_num} won")

                    if (match["player1rank"] == 0):
                        logger.error(f"{video_id} {count:10d} - round is over but player 1 rank is 0")
                    if (match["player2rank"] == 0):
                        logger.error(f"{video_id} {count:10d} - round is over but player 2 rank is 0")

                    if (cnt < 3):
                        round=new_round()
                        round["player1_rounds"]=rounds_won[0]
                        round["player2_rounds"]=rounds_won[1]
                        round_num+=1
                        skipFrames = 10
                    break
                else:
                    logger.debug(f"{video_id} {count:10d} not finding diff of one with cnt: {cnt} player {player_num}")

            if (round["player1_rounds"] == 3 or round["player2_rounds"] == 3):
                state="before"
                round=new_round()
                rounds_won=[0, 0]
                round_num = 1
                match={}
                match["id"] = uuid.uuid4()
                logger.debug(f"{video_id} {count:10d} - match finished")
                skipFrames=2

        if (state == "before"):
            count+=int(frame_rate * interval*4)
        else:
            count+=int(frame_rate * interval)

    if (state != "before"):
        logger.error(f"{video_id} {count:10d} - premature match aborted")
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
    if (vf_analytics.is_excellent(frame)):
        print(f"player {player_num} got excellent")
        round[f"player{player_num}_excellent"] = 1

def process_ko(player_num, frame, round):
    if (vf_analytics.is_ko(frame)):
        print(f"player {player_num} got ko")
        round[f"player{player_num}_ko"] = 1

def process_ringout(player_num, frame, round):
    if (vf_analytics.is_ringout(frame)):
        print(f"player {player_num} got ringout")
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
    p = pathlib.Path('match_data.csv')
    if (not p.is_file()):
        with open('match_data.csv', 'a') as the_file:
            the_file.write('vid,match_id,stage,player1ringname,player1rank,player1character,player2ringname,player2rank,player2character,round_num,player1_rounds_won,p1ko,p1ro,p1ex,player2_rounds_won,p2ko,p2ro,p2ex\n')
    with open('match_data.csv') as f:
        if video_id in f.read():
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

    extract_frames(video_path, 1, video_folder, video_id, jpg_folder)  # Extract a frame every 7 seconds


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
def main(video_url = None, playlists_file=None, playlist_file=None):

    if (video_url is not None and "list=" in video_url):
        process_playlist(video_url)
        return

    if (video_url is not None):
        analyze_video(video_url)
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
    logging.basicConfig(filename='analyze_youtube.log', encoding='utf-8', level=logging.DEBUG)

    parser=argparse.ArgumentParser(description="Download and extract match data from VF5ES videos")
    parser.add_argument('--youtube-auth', default=True)
    parser.add_argument('--video_url', default=None, help="URL for youtube video or playlist to process")
    parser.add_argument('--playlists_file', default=None, help="Local file with list of playlists to process")
    parser.add_argument('--playlist_file', default=None, help="Local file with list of YouTube videos to process")
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

    #main(video_url)
    main(video_url=video_url, playlists_file=playlists_file, playlist_file=playlist_file)