import os
from timeit import default_timer as timer
import threading
import uuid
import sys
import logging
import argparse
import pathlib
import time
import ffmpeg
import cv2
import psutil
import numpy as np
import VideoCaptureAsync
import vf_analytics
import youtube_helper
import vf_cv
import traceback

DONT_SAVE = True

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="vf_match_analyzer.log", encoding="utf-8", level=logging.INFO
)

resize_video = False
youtube_auth = True
force_append = False
video_folder_param = None

time_cv = vf_cv.Timer()
winning_round = vf_cv.WinningRound()
player_rank = vf_cv.PlayerRank()
character = vf_cv.Character()


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


def save_image(out_filename, frame):
    try:
        cv2.imwrite(out_filename, frame)
    except Exception as e:
        logger.error(f"Error writing to image file {out_filename}")
        logger.error(repr(e))


def save_cam_frame(jpg_folder, original_frame, frame, count_int, suffix):
    if DONT_SAVE:
        return
    if not os.path.exists(jpg_folder + "/original/"):
        os.makedirs(jpg_folder + "/original/")

    hdd = psutil.disk_usage("/")
    if hdd.free < 10567308288:
        return

    original_thread = None
    original_out_filename = (
        jpg_folder + "/original/" + str(f"{count_int}_{suffix}") + ".png"
    )
    if not os.path.isfile(original_out_filename):
        original_thread = threading.Thread(
            target=save_image, args=(original_out_filename, original_frame)
        )
        original_thread.start()

    normal_thread = None
    out_filename = jpg_folder + "/" + str(f"{count_int}_{suffix}") + ".png"
    if not os.path.isfile(out_filename):
        normal_thread = threading.Thread(target=save_image, args=(out_filename, frame))
        normal_thread.start()

    if original_thread is not None:
        original_thread.join()

    if normal_thread is not None:
        normal_thread.join()


# Step 2: Extract frames from the video
@profile
def extract_frames(
    cap,
    interval,
    video_id="n/a",
    jpg_folder="jpg",
    cam=-1,
    frame_rate=None,
    frame_count=None,
):
    end_frame = None
    if end_frame is None or end_frame > frame_count:
        end_frame = frame_count

    startFrame = 1
    count = startFrame

    state = "before"
    round = new_round()
    rounds_won = [0, 0]
    match = {}
    round_num = 1

    match["id"] = uuid.uuid4()

    skipFrames = 0

    if cam != -1:
        jpg_folder = "assets/jpg/cam"
        if not os.path.exists(jpg_folder):
            os.makedirs(jpg_folder)

    # fight_time = None
    # elapsed_time = timer() - start # in seconds
    vf_analytics.resolution = "480p"
    actual_count = 0

    old_time = None
    timestr = None
    time_matches = 0
    matches_processed = 0

    time_seconds = None
    while count < end_frame or cam != -1:

        count_int = int(count)

        # use epoch time for cam
        if cam != -1:
            count_int = int(time.time() * 1000)
            count = count_int

        frame = None
        if skipFrames > 0 and cam != -1:
            skipFrames -= 1
            if cam != -1:
                cap.read()
                time.sleep(interval)
            continue
        if skipFrames > 0 and cam == -1:
            count += int((frame_rate * interval) * skipFrames)
            count_int = int(count)
            skipFrames = 0

        original_frame = None

        if (
            DONT_SAVE == False
            and cam == -1
            and os.path.isfile(jpg_folder + "/" + str(f"{count_int:13d}") + ".jpg")
        ):
            try:
                filename = jpg_folder + "/" + str(f"{count_int:13d}") + ".jpg"
                frame = cv2.imread(filename)
            except Exception as e:
                logger.error(
                    f"{video_id} {count:13d} [ERROR] - error reading from image file",
                    file=sys.stderr,
                )
                logger.error(repr(e))
                continue
        else:
            ret = None
            frame = None

            if cam != -1:
                actual_count = count - 1

            while actual_count < count_int:
                # ret, frame = cap.read()
                frame = cap.read()
                actual_count = actual_count + 1

            if not ret and frame is None:
                print("could not read frame")
                logger.warning(f"Skipping frame {count:13d} because no return")
                continue

            # if (cam == -1):
            # frame = vf_analytics.remove_black_border(frame, resize_height=480)
            # else:

        if frame is None:
            continue

        original_frame = frame
        height = frame.shape[0]  # Get the dimensions of the frame

        frame_480p = None

        if state == "before":
            logger.debug(f"BEFORE - searching for vs frame count {count}")
            print(f"BEFORE - searching for vs frame count {count}")

            stage = None
            if vf_analytics.is_vs(frame):
                if height != 480:
                    frame_480p = cv2.resize(frame, (854, 480))

                stage = vf_analytics.get_stage(frame_480p)
                if stage is None:
                    save_cam_frame(
                        jpg_folder, original_frame, frame, count, "invalid_is_vs"
                    )

            if stage is not None:
                match["stage"] = stage
                state = "vs"
                logger.debug(
                    f"{video_id} {count:13d} - got stage {stage} and setting to vs"
                )

                if cam == -1:
                    print(
                        f"{video_id} {count:13d} - got stage {stage} and setting to vs"
                    )
                else:
                    print(
                        f"camera: {cam} {count:13d} - got stage {stage} and setting to vs"
                    )
            else:
                count += int(frame_rate * interval * 40)
                del frame
                del original_frame
                continue

        #        if (height != 480 and frame_480p is None):
        #            frame = cv2.resize(frame, (854, 480))
        #        elif (height == 480):
        #            frame = frame_480p

        # vf_analytics.resolution = 480

        if state == "vs":
            if match.get("player1character") is None:
                character.set_frame(frame)
                player1character = character.get_character_name(1)
                if player1character is not None:
                    match["player1character"] = player1character
                    logger.debug(
                        f"{video_id} {count:13d} - player 1 character {player1character}"
                    )
                    save_cam_frame(
                        jpg_folder,
                        original_frame,
                        frame,
                        count,
                        f"player1_character-{player1character}",
                    )

            if match.get("player2character") is None:
                character.set_frame(frame)
                player2character = character.get_character_name(2)
                if player2character is not None:
                    match["player2character"] = player2character
                    logger.debug(
                        f"{video_id} {count:13d} - player 2 character {player2character}"
                    )
                    save_cam_frame(
                        jpg_folder,
                        original_frame,
                        frame,
                        count,
                        f"player2_character-{player2character}",
                    )

            if not "player1ringname" in match or match["player1ringname"] is None:
                player1ringname = vf_analytics.get_ringname(1, frame)
                match["player1ringname"] = player1ringname
                logger.debug(f"{video_id} {count:13d} - player 1 is {player1ringname}")

            if not "player2ringname" in match or match["player2ringname"] is None:
                player2ringname = vf_analytics.get_ringname(2, frame)
                match["player2ringname"] = player2ringname
                logger.debug(f"{video_id} {count:13d} - player 2 is {player2ringname}")

            if "stage" not in match:
                logger.debug(f"{video_id} {count:13d} - looking for stage")
                stage = vf_analytics.get_stage(frame)
                if stage is not None:
                    match["stage"] = stage
                    logger.debug(f"{video_id} {count:13d} - stage {stage}")

            if got_all_vs_info(match):
                state = "fight"
                logger.debug(f"{video_id} {count:13d} - fight")
                print_csv(match, round, "0", video_id, count, "n/a")

                skipFrames = (int)(25 / interval)
                # skipFrames for 1
                # skipFrames=28
                print(f"got all match info: {count:13d} - fight")
                save_cam_frame(jpg_folder, original_frame, frame, count, "start")

                del frame
                del original_frame

                continue
            # else:
            # save_cam_frame(jpg_folder, original_frame, frame, count, "vs")

        if state == "fight":
            old_time_seconds = time_seconds

            time_cv.set_frame(frame)
            time_seconds = time_cv.get_time_seconds(frame)
            if (
                (time_seconds == "43" or time_seconds == "44" or time_seconds == "45")
                or (time_seconds != old_time_seconds)
                or old_time_seconds is None
            ):
                count += int(frame_rate * interval)

                del frame
                del original_frame

                continue

            time_ms = time_cv.get_time_ms()

            old_time = timestr
            timestr = f"{time_seconds}.{time_ms}"

            #            print(timestr)
            #            cv2.imshow("image", frame)
            # cv2.waitKey()

            if old_time == timestr and timestr != "45.00" and time_seconds != "":
                time_matches = time_matches + 1
            else:
                time_matches = 0

            player_num = 0

            if time_matches >= 2:
                if height != 480 and frame_480p is None:
                    frame = cv2.resize(frame, (854, 480))
                elif height == 480:
                    frame = frame_480p

                winning_round.set_frame(frame)
                player_num = winning_round.is_winning_round()
                # if (player_num != 0):
                # save_cam_frame(jpg_folder, original_frame, frame, count, f"fight_{time_seconds}_{time_ms}_won")
                # else:
                # save_cam_frame(jpg_folder, original_frame, frame, count, f"fight_{time_seconds}_{time_ms}")
            # save_cam_frame(jpg_folder, original_frame, frame, count, f"fight_{time_seconds}_{time_ms}")
            else:
                count += 1
                del frame
                del original_frame

                continue

            if player_num == 0:
                # logger.debug(f"{count_int} could not determine which player won so skipping")
                # save_cam_frame(jpg_folder, original_frame, frame, count, f"fight_{time_seconds}_{time_ms}")
                count += 1
                del frame
                del original_frame

                continue

            # save_cam_frame(jpg_folder, original_frame, frame, count, "fight")
            is_excellent = vf_analytics.is_excellent(frame)
            is_ko = not is_excellent and vf_analytics.is_ko(frame)
            is_ro = not is_excellent and not is_ko and vf_analytics.is_ringout(frame)

            # if (not is_excellent and not is_ko and not is_ro):
            # logger.warning(f"{video_id} {count} - unknown way to win the round!")
            # count = count +1
            # continue

            player_rank.set_frame(frame)
            if "player1rank" not in match or match["player1rank"] == 0:
                try:
                    player1rank = player_rank.get_player_rank(1)
                    match["player1rank"] = player1rank
                    logger.debug(f"{video_id} {count:13d} - player1rank {player1rank}")
                except:
                    match["player1rank"] = 0

            if "player2rank" not in match or match["player2rank"] == 0:
                try:
                    player2rank = player_rank.get_player_rank(2)
                    match["player2rank"] = player2rank
                    logger.debug(f"{video_id} {count:13d} - player2rank {player2rank}")
                except:
                    match["player2rank"] = 0

            # print(f"{timestr} vs old {old_time}")

            if timestr != old_time:
                count += int(frame_rate * interval) * 3
                del frame
                del original_frame

                continue

            logger.debug(f"{video_id} {count:013d} - player {player_num} won the match")

            if is_excellent:
                round[f"player{player_num}_excellent"] = 1
                print(f"{count} got EX for player {player_num}")
            elif is_ko:
                round[f"player{player_num}_ko"] = 1
                print(f"{count} got KO for player {player_num}")
            elif is_ro:
                round[f"player{player_num}_ringout"] = 1
                print(f"{count} got RO for player {player_num}")
            else:
                print(f"{count} unknown way to victory for {player_num} skipping")
                count += int(frame_rate * interval)

                save_cam_frame(jpg_folder, original_frame, frame, count, "unknown_skip")
                del frame
                del original_frame

                continue

            rounds_won[player_num - 1] = rounds_won[player_num - 1] + 1
            round[f"player{player_num}_rounds"] = (
                round[f"player{player_num}_rounds"] + 1
            )

            try:
                timestr = None
                try:
                    time_seconds = vf_analytics.get_time_seconds(frame)
                    time_ms = time_cv.get_time_ms()
                    timestr = f"{time_seconds}.{time_ms}"
                except:
                    timestr = "na"

                print_csv(match, round, round_num, video_id, count, timestr)

                suffix = ""
                if is_excellent:
                    suffix = f"excellent_for_player{player_num}"
                elif is_ro:
                    suffix = f"ringout_for_player{player_num}"
                elif is_ko:
                    suffix = f"knockout_for_player{player_num}"
                else:
                    suffix = f"unknownwin_for_player{player_num}"

                save_cam_frame(
                    jpg_folder,
                    original_frame,
                    frame,
                    count,
                    f"{rounds_won[0]}_{rounds_won[1]}_{suffix}_{timestr}",
                )
            except:
                logger.error(f"{video_id} {count:13d} ERROR write to csv")
            logger.debug(
                f"{video_id} {count:13d} - round {round_num} finished player {player_num} won"
            )

            if match["player1rank"] == 0:
                logger.error(
                    f"{video_id} {count:13d} - round is over but player 1 rank is 0"
                )
            if match["player2rank"] == 0:
                logger.error(
                    f"{video_id} {count:13d} - round is over but player 2 rank is 0"
                )

            if round[f"player{player_num}_rounds"] < 3:
                round = new_round()
                round["player1_rounds"] = rounds_won[0]
                round["player2_rounds"] = rounds_won[1]
                round_num += 1

                if cam == -1:
                    skipFrames = 10 / interval
                time_matches = 0
                # print(f"{count} new round")
            else:
                state = "before"
                round = new_round()
                rounds_won = [0, 0]
                round_num = 1
                match = {}
                match["id"] = uuid.uuid4()
                logger.debug(f"{video_id} {count:13d} - match finished")
                skipFrames = 2
                matches_processed += 1

                # elapsed_time = timer() - fight_time # in seconds
                # print(f"time in fight state: {elapsed_time}")

        # if (cam != -1):
        # time.sleep(0.25)

        count += int(frame_rate * interval)
        del frame
        del original_frame

    if state != "before":
        logger.error(f"{video_id} {count:13d} - premature match aborted")

    # hdd = psutil.disk_usage("/")

    # if hdd.free < 10567308288:
    # os.remove(video_path)

    # cap.release()
    return (count, matches_processed)


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


def print_csv(match, round, round_num, video_id, frame_count, time):
    with open(f"match_data_{video_id}.csv", "a") as f:
        if video_id is None:
            f.write("cam")
        else:
            f.write(video_id)

        f.write(",")
        f.write(str(frame_count))
        f.write(",")
        f.write(str(match["id"]))
        f.write(",")
        if not "stage" in match or match["stage"] is None:
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

        f.write(",")
        try:
            f.write(str(time))
        except:
            f.write("0")

        f.write("\n")


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
    if not "stage" in match:
        return False
    if not "player1character" in match:
        return False
    if not "player2character" in match:
        return False
    if not "player1ringname" in match:
        return False
    if not "player2ringname" in match:
        return False

    return True


# Step 3: Perform OCR on specific regions
def perform_ocr_on_frames(frames, video_id="n/a"):
    # height, width = list(frames.keys())[0].shape

    # height, width, _ = frames[0].shape  # Get the dimensions of the frame
    # print(f"{width} x {height}")

    # originalWidth=640
    # originalHeight=359

    return


def analyze_video(url, cam=-1):
    start = timer()
    p = pathlib.Path("match_data.csv")
    if not p.is_file():
        with open("match_data.csv", "a") as the_file:
            the_file.write(
                "vid,match_id,stage,player1ringname,player1rank,player1character,player2ringname,player2rank,player2character,round_num,player1_rounds_won,p1ko,p1ro,p1ex,player2_rounds_won,p2ko,p2ro,p2ex\n"
            )

    video_id = None
    video_folder = None
    video_path = None
    jpg_folder = None

    if url is not None:
        video_id = youtube_helper.get_youtube_video_id(url)
        if pathlib.Path(f"match_data_{video_id}.csv").is_file():
            print(f"Skipping {video_id} since it's already in match data")
            return

        resolution = None
        jpg_folder = None

        if not os.path.isfile(
            f"assets/videos/{video_id}_480p/video.mp4"
        ) and not os.path.isfile(f"assets/videos/{video_id}_720p/video.mp4"):
            ys = youtube_helper.get_stream(url)
            resolution = ys.resolution
            vf_analytics.resolution = resolution

            if video_folder_param is not None:
                video_folder = video_folder_param
            else:
                video_folder = f"assets/videos/{video_id}_{resolution}/"
            video_path = f"assets/videos/{video_id}_{resolution}/video.mp4"

            if not os.path.exists(video_folder):
                os.makedirs(video_folder)

            if not os.path.isfile(video_path):
                try:
                    logger.debug(f"Downloading video {url} at {resolution}")
                    temp_path = youtube_helper.download_video(
                        ys, video_id, resolution=resolution
                    )

                    print(f"Renaming video after download: {temp_path} to {video_path}")
                    if resolution != "480p" and resize_video:
                        ffmpeg.input(temp_path).output(
                            video_path, vf="scale=854:480"
                        ).run()
                        os.remove(temp_path)
                    else:
                        os.rename(temp_path, video_path)
                except Exception as e:
                    print(f'error downloading "{url}" ')
                    print(ys)
                    print(repr(e))
                    return None
            else:
                print(f"Not downloading because exists: {video_path}")
        else:
            if os.path.isfile(f"assets/videos/{video_id}_480p/video.mp4"):
                resolution = "480p"
            else:
                resolution = "720p"
            video_path = f"assets/videos/{video_id}_{resolution}/video.mp4"

    jpg_folder = f"assets/jpg/{video_id}_{resolution}"
    if not os.path.exists(jpg_folder):
        os.makedirs(jpg_folder)

    print("Extracting frames")
    start = timer()

    vf_analytics.resolution = "480p"
    resolution = "480p"

    fps = 0.05
    frame_rate = None
    frame_count = None

    try:
        if video_path is not None:
            # cap = cv2.VideoCapture(video_path )
            cap = VideoCaptureAsync.VideoCaptureAsync(video_path)
            frame_rate = cap.get_frame_rate()
            frame_count = cap.get_frame_count()
        else:
            cap = cv2.VideoCapture(cam)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            if not cap.isOpened():
                print(f"Failed to open CAM {cam}")
                return

            frame_rate = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        processed = 0
        matches_processed = 0

        processed, matches_processed = extract_frames(
            cap,
            fps,
            video_id,
            jpg_folder,
            cam=cam,
            frame_rate=frame_rate,
            frame_count=frame_count,
        )  # Extract a frame every 7 seconds
    except Exception as e:
        logger.error(f"An exception occured {e}")
        logger.error(repr(e))
        logger.error(traceback.format_exc())
    finally:
        cap.release()

    elapsed_time = timer() - start  # in seconds
    fps = processed / elapsed_time
    mps = 0
    if matches_processed != 0:
        mps = elapsed_time / matches_processed

    logger.info(
        f"{elapsed_time} seconds to run  {fps} FPS ----- {mps} seconds per match   {matches_processed} matches finished"
    )


def process_playlist(playlist):
    urls = youtube_helper.get_video_urls_from_playlist(playlist)
    for url in urls:
        try:
            analyze_video(url)
        except Exception as e:
            logger.error(f"Error processing {url}")
            logger.error(repr(e))
            print(f"Error processing {url}")
            print(repr(e))


def process_videos_list(urls):
    for url in urls:
        try:
            analyze_video(url)
        except Exception as e:
            logger.error(f"Error processing {url}")
            logger.error(repr(e))
            print(f"Error processing {url}")
            print(repr(e))


def process_playlists(playlist_array):
    for playlist in playlist_array:
        process_playlist(playlist)


# Main function to run the whole process
def main(video_url=None, playlists_file=None, playlist_file=None, cam=-1):

    if video_url is not None and "list=" in video_url:
        process_playlist(video_url)
        return

    if video_url is not None:
        analyze_video(video_url)
        return

    if cam != -1:
        analyze_video(cam=cam, url=None)
        return

    if playlists_file is not None:
        playlists = []
        with open(playlists_file) as my_file:
            for line in my_file:
                if line is not None:
                    line = line.strip()
                    playlists.append(line)
        process_playlists(playlists)
        return

    if playlist_file is not None:
        videos = []
        with open(playlist_file) as my_file:
            for line in my_file:
                if line is not None:
                    line = line.strip()
                    videos.append(line)
        process_videos_list(videos)
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download and extract match data from VF5ES videos"
    )
    parser.add_argument("--youtube-auth", default=True)
    parser.add_argument(
        "--video_url", default=None, help="URL for youtube video or playlist to process"
    )
    parser.add_argument(
        "--playlists_file",
        default=None,
        help="Local file with list of playlists to process",
    )
    parser.add_argument(
        "--playlist_file",
        default=None,
        help="Local file with list of YouTube videos to process",
    )
    parser.add_argument("--force_append", default=None, help="Force overwrite videos")
    parser.add_argument("--cam", default=None, help="Set to capture from camera")
    # parser.add_argument('--resolution', default='1080p', help="video resolution 10809p, 480p, 360p")

    args = parser.parse_args()

    video_url = None
    try:
        video_url = vars(args)["video_url"]
        if video_url is not None:
            video_url = video_url.strip()
    except:
        video_url = None

    playlists_file = None
    try:
        playlists_file = vars(args)["playlists_file"]
        if playlists_file is not None:
            playlists_file = playlists_file.strip()
    except:
        playlists_file = None

    playlist_file = None
    try:
        playlist_file = vars(args)["playlist_file"]
        if playlist_file is not None:
            playlist_file = playlist_file.strip()
    except:
        playlist_file = None

    try:
        fa = vars(args)["force_append"]
        if fa is not None:
            force_append = True
    except:
        force_append = False

    cam = None
    try:
        cam = vars(args)["cam"]
        if cam is not None:
            cam = cam.strip()
    except:
        cam = None

    video_folder_param = None
    try:
        video_folder_param = vars(args)["video_folder"]
        if video_folder_param is not None:
            video_folder_param = video_folder_param.strip()
    except:
        video_folder_param = None

    # main(video_url)
    cam_int = -1
    if cam is not None:
        cam_int = int(cam)

    # main(video_url)
    main(
        video_url=video_url,
        playlists_file=playlists_file,
        playlist_file=playlist_file,
        cam=cam_int,
    )
