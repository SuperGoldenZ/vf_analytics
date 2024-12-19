import os
from timeit import default_timer as timer
import logging
import argparse
import pathlib
import traceback
import ffmpeg
import cv2
import VideoCaptureAsync
import vf_cv.match_analyzer
import vf_cv.revo
import vf_analytics
import vf_data
import vf_data.match
import youtube_helper


FORCE_DELETE_VIDEO = True
PROCESS_STREAMED_VIDEOS = True
FORCE_SINGLE_MATCH_PER_VIDEO = True
STOP_ON_FIRST_ERROR = False
PROCESS_VS_ONLY = False
PROCESS_SHUN_ONLY = True

logger = logging.getLogger(__name__)
#logging.basicConfig(
    #filename="vf_match_analyzer.log",
    #encoding="utf-8",
    #level=logging.INFO,
    #format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
#)

resize_video = False
youtube_auth = True
force_append = False
video_folder_param = None


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


def print_csv(
    match: vf_data.Match,
):
    with open(f"match_data_{match.video_id}.csv", "a") as f:
        f.write(str(match))

def print_csv_match_only(
    match: vf_data.Match,
):
    with open(f"matches.csv", "a") as f:
        f.write(str(match))

def print_error_csv(match: vf_data.Match, resolution, error_message):
    with open("errors.csv", "a") as f:
        f.write(
            f"{match.video_id},{resolution},{match.player1character},{match.player1rank},{match.player2character},{match.player2rank},{match.stage},{error_message}\n"
        )


def get_saved_video_resolution(video_id, url=None):
    if os.path.isfile(f"assets/videos/{video_id}_480p/video.mp4"):
        return 480
    if os.path.isfile(f"assets/videos/{video_id}_1080p/video.mp4"):
        return 1080
    if os.path.isfile(f"assets/videos/{video_id}_720p/video.mp4"):
        return 720
    if os.path.isfile(url):
        return 1080
    return 0


def check_string_in_file(file_path, string_to_search):
    if not os.path.exists(file_path):
        return False

    with open(file_path, "r") as file:
        for line in file:
            if string_to_search in line:
                return True
    return False

def is_youtube_url(url):
    return "youtube" in url

def analyze_video(url, cam=-1, process_vs_only=False):
    print(f"\n=========\nAnalyze video {url} - START")
    start = timer()

    video_id = None
    video_folder = None
    video_path = None
    jpg_folder = None
    error_message = None
    match_analyzer = None
    saved_video_resolution = None
    ys = None
    resolution=None
    temp_title = None    
    
    if url is not None:
        if (is_youtube_url(url)):
            video_id = youtube_helper.get_youtube_video_id(url)
            temp_title = read_video_title(video_id)
            
            if (PROCESS_SHUN_ONLY and temp_title is not None and "舜" not in temp_title):
                print("skipping because not shun")
                return True
        else:
            video_id = pathlib.Path(url).stem
        
        if pathlib.Path(f"match_data_{video_id}.csv").is_file():
            print(f"\tSkipping {video_id} since it's already in match data")
            return

        if check_string_in_file("matches.csv", video_id):
            print(f"\tSkipping {video_id} since it's already in matches.csv")
            return
        
        error_string = f"{video_id}"
        if check_string_in_file("vf_analytics.log", error_string):
            print(f"\tSkipping {video_id} since it's already in log as error")
            return

        error_string = f"{video_id}_720p/video.mp4 since didn't process matches"
        if check_string_in_file("vf_analytics.log", error_string):
            print(f"\tSkipping {video_id} since didn't process fully")
            return

        resolution = None
        jpg_folder = None

        saved_video_resolution = get_saved_video_resolution(video_id, url)
        resolution = f"{saved_video_resolution}p"
        ys = None

        if saved_video_resolution == 0:
            # """Video not saved locally, download"""
                        
            ys = youtube_helper.get_stream(url, process_vs_only=process_vs_only)
            resolution = ys.resolution
            vf_analytics.resolution = resolution

            if video_folder_param is not None:
                video_folder = video_folder_param
            else:
                video_folder = f"assets/videos/{video_id}_{resolution}/"
            video_path = f"assets/videos/{video_id}_{resolution}/video.mp4"

            if not os.path.exists(video_folder) and not PROCESS_STREAMED_VIDEOS:
                os.makedirs(video_folder, exist_ok=True)

            if not os.path.isfile(video_path) and not PROCESS_STREAMED_VIDEOS:
                try:
                    print(f"\tDownloading video {url} at {resolution}")
                    logger.debug(f"Downloading video {url} at {resolution}")
                    temp_path = youtube_helper.download_video(ys, video_id)

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
            elif not PROCESS_STREAMED_VIDEOS:
                print(
                    f"Not downloading because exists: {video_path} and process steram {PROCESS_STREAMED_VIDEOS}"
                )
        else:
            video_path = f"assets/videos/{video_id}_{resolution}/video.mp4"
            print(f"found video and loading from {video_path}")

    start = timer()

    vf_analytics.resolution = "480p"

    fps = 0.05
    frame_rate = None
    frame_count = None

    processed = 0
    matches_processed = 0
    cap = None

    try:
        if video_path is not None:
            if PROCESS_STREAMED_VIDEOS and saved_video_resolution == 0:
                # print(f"Processing strem for {ys.url}")
                cap = VideoCaptureAsync.VideoCaptureAsync(ys.url)
            elif os.path.isfile(video_path):
                cap = VideoCaptureAsync.VideoCaptureAsync(video_path)
            elif os.path.isfile(url):
                cap = VideoCaptureAsync.VideoCaptureAsync(url)
            else:
                raise Exception(f"File not found {url}")
            
            frame_rate = round(cap.get_frame_rate())
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

        youtube_video_title = None
        if ys is not None:
            youtube_video_title = ys.title
            save_video_title(video_id, youtube_video_title)
            save_video_url(video_id, resolution, frame_rate, ys.url)
        if (ys is not None and PROCESS_SHUN_ONLY and "舜" not in ys.title):
            print("skipping because not shun")
            return True
        
        if ys is None or ys.title is None:
            youtube_video_title = read_video_title(video_id)

        jpg_folder = f"assets/jpg/{video_id}_{resolution}"
        if not os.path.exists(jpg_folder):
            os.makedirs(jpg_folder, exist_ok=True)

        if (saved_video_resolution == 0):
            print(f"\tCreating match for youtube video title {ys.title} {frame_rate}FPS ")
        else:
            print(f"\tCreating from saved video")
        match_analyzer = vf_cv.match_analyzer.MatchAnalyzer(
            cap,
            logger,
            jpg_folder=jpg_folder,
            interval=fps,
            frame_rate=frame_rate,
            youtube_video_title=youtube_video_title,
            process_vs_only=process_vs_only
        )
        processed = 0
        matches_processed = 0
        frames_processed = -1
        while frames_processed != 0:
            print(f"\tProcessing match {matches_processed+1}")
            frames_processed = match_analyzer.analyze_next_match(
                video_id=video_id,
                cam=cam,
                frame_count=frame_count,
                start_frame=processed,                
            )  # Extract a frame every 7 seconds

            if (process_vs_only):
                print_csv_match_only(match_analyzer.match)
                processed += frames_processed
                matches_processed += 1
                continue

            if frames_processed != 0:
                print_csv(match_analyzer.match)
                processed += frames_processed
                matches_processed += 1

                if FORCE_SINGLE_MATCH_PER_VIDEO:
                    break
    except vf_cv.PrematureMatchFinishException as e:
        error_message = str(e)
        print(f"Premature Match End exception occured {e} processing video {video_id}")
        logger.error(
            f"Premature match end exception occured {e} processing video {video_id}"            
        )
        print_error_csv(match_analyzer.match, resolution, "premature_end")
        if (STOP_ON_FIRST_ERROR):
            exit("premature_end")
    except vf_cv.UnrecognizeTimeDigitException as e:
        logger.error(f"An exception occured {e} processing video {video_id}")
        print(
            f"UnrecognizedTimeDigit exception occured {e} processing video {video_id}"
        )
        print_error_csv(match_analyzer.match, resolution, "unrecognized_time_digit")
        if (STOP_ON_FIRST_ERROR):
            exit("unrecognized_player_rank")        
    except vf_cv.UnrecognizePlayerRankException as e:
        error_message = str(e)
        logger.error(f"An exception occured {e} processing video {video_id}")
        print(
            f"UnrecognizedPlayerRank exception occured {e} processing video {video_id}"
        )
        print_error_csv(match_analyzer.match, resolution, "unrecognized_player_rank")
        if (STOP_ON_FIRST_ERROR):
            exit("unrecognized_player_rank")
    except Exception as e:
        error_message = str(e)
        print(f"\tAnother exception occured {e} processing video {video_id}")
        logger.error(f"An exception occured {e} processing video {video_id}")
        logger.error(repr(e))
        logger.error(traceback.format_exc())
        if (match_analyzer is not None):
            print_error_csv(match_analyzer.match, resolution, "other")
        if (STOP_ON_FIRST_ERROR):
            exit("other error")
    finally:
        # print("\tFinally - Releasing cap")
        cap.release()
        # print("\tFinally - Checking to delete")
        if (saved_video_resolution == 0 and FORCE_DELETE_VIDEO or error_message is None) and os.path.isfile(video_path):
            os.remove(video_path)

        if (saved_video_resolution == 0 and FORCE_DELETE_VIDEO) and os.path.isfile(video_path):
            os.remove(video_path)

        # if (error_message is not None):
        # exit()
    try:
        elapsed_time = timer() - start  # in seconds
        fps = processed / elapsed_time
        mps = 0
        if matches_processed != 0:
            mps = elapsed_time / matches_processed

        logger.info(
            f"{elapsed_time} seconds to run  {fps} FPS ----- {mps} seconds per match   {matches_processed} matches finished resoution: {resolution} {round(frame_rate)}FPS"
        )
        print(
            f"{elapsed_time} seconds to run  {fps} FPS ----- {mps} seconds per match   {matches_processed} matches finished resolution: {resolution} {round(frame_rate)} FPS"
        )
    except Exception as e:
        print("Another exception")
        print(e)
        error_message = str(e)

    return error_message is None


def process_playlist(playlist, process_vs_only=False):
    urls = youtube_helper.get_video_urls_from_playlist(playlist)
    success = 0
    errors = 0

    for url in urls:
        try:
            # analyze_video(url)
            # success = success + 1
            print(url)
        except Exception as e:
            errors = errors + 1
            logger.error(f"Error processing {url}")
            logger.error(repr(e))
            # print(f"Error processing {url}")
            # print(repr(e))
        finally:
            total = success + errors
            # print(f"{success} success {error} errors {(success/total)*100} success rate")


def process_videos_list(urls, process_vs_only=False):
    success = 0
    errors = 0

    for url in urls:
        try:
            result = analyze_video(url, process_vs_only=process_vs_only)
            if result:
                success = success + 1
            else:
                errors = errors + 1
        except Exception as e:
            errors = errors + 1
            logger.error(f"Error processing {url}")
            logger.error(repr(e))
            print(f"Error processing {url}")
            print(repr(e))
        finally:
            total = success + errors
            print(
                f"{success} success {errors} errors {(success/total)*100} success rate"
            )
            # if (total > 30 and (success/total) < 0.95 ):
            # print("Below 95% success rate")
            # exit()


def process_playlists(playlist_array):
    for playlist in playlist_array:
        process_playlist(playlist)

def read_video_title(video_id):
    video_path = f"assets/videos/"
    title_file = f"{video_path}{video_id}.title"

    s = None
    try:
        with open(title_file) as f: s = f.read()
    except:
        s = None
    
    return s


def save_video_title(video_id, title):    
    video_path = f"assets/video_meta/{video_id}/"

    if not os.path.exists(video_path):
        os.makedirs(video_path, exist_ok=True)

    title_file = f"{video_path}{video_id}.title.txt"

    with open(title_file, "w") as f:
        f.write(
            title
        )

def save_video_url(video_id, resolution, frame_rate, url):
    video_path = f"assets/video_meta/{video_id}/"

    if not os.path.exists(video_path):
        os.makedirs(video_path, exist_ok=True)

    title_file = f"{video_path}{video_id}_{resolution}_{frame_rate}fps.url.txt"

    with open(title_file, "w") as f:
        f.write(
            url
        )

# Main function to run the whole process
def main(video_url=None, playlists_file=None, playlist_file=None, cam=-1, process_vs_only = False, revo = False):

    if (revo):
        vf_cv.REVO.capture_window()

    if video_url is not None and "list=" in video_url:
        process_playlist(video_url, process_vs_only)
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
        process_videos_list(videos, process_vs_only=process_vs_only)
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
    parser.add_argument("--revo", default=None, help="Set to capture from R.E.V.O. in Windows")
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

    cam_int = -1
    if cam is not None:
        cam_int = int(cam)

    revo = vars(args)["revo"]

    main(
        video_url=video_url,
        playlists_file=playlists_file,
        playlist_file=playlist_file,
        cam=cam_int,
        process_vs_only=PROCESS_VS_ONLY,
        revo=revo is not None
    )
