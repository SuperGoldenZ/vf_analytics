import os
import shutil

from timeit import default_timer as timer

import logging
import argparse
import pathlib
import traceback
import cv2
import vf_cv.video_capture_async
import vf_cv.match_analyzer
import vf_analytics
import vf_data
import vf_data.match
import youtube_helper
import vf_cv.config
import time

from obs import ObsHelper
from datetime import datetime
from window_controller import WindowController

config: vf_cv.Config = vf_cv.Config.load_config("default.cfg")

FORCE_DELETE_VIDEO = True
FORCE_SINGLE_MATCH_PER_VIDEO = False
STOP_ON_FIRST_ERROR = False
PROCESS_VS_ONLY = False
PROCESS_SHUN_ONLY = False

obs_helper = None
try:
    obs_helper = ObsHelper()
except Exception as e:
    print("could not init obs helper")
    print(e)
    print(traceback.format_exc())

logger = logging.getLogger(__name__)

logging.basicConfig(
    filename="vf_match_analyzer.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
)

resize_video = False
youtube_auth = True
force_append = False


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
    try:
        out_filename = f"match_data_{match.make_id()}.csv"

        if pathlib.Path(out_filename).is_file():
            out_filename = out_filename + ".duplicate"

        with open(out_filename, "w", encoding="utf-8", errors="replace") as f:
            f.write(str(match))
    except Exception as e:
        logger.error(f"error printing to csv {e}")


def print_csv_match_only(
    match: vf_data.Match,
):
    with open(f"matches.csv", "a", encoding="utf-8", errors="replace") as f:
        f.write(str(match))


def print_error_csv(match: vf_data.Match, resolution, error_message, match_number=0):
    try:
        with open("errors.csv", "a", encoding="utf-8", errors="replace") as f:
            f.write(
                f"{match.video_id},{match_number}, {resolution},{match.player1character},{match.player1rank},{match.player1ringname},{match.player2character},{match.player2rank},{match.player2ringname},{match.stage},{error_message}\n"
            )
    except:
        logger.error("could not print error CSV")


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
    global obs_helper

    print(f"\n=========\nAnalyze video {url} - START")
    start = timer()

    video_id = None
    video_folder = None
    video_path = None

    error_message = None
    match_analyzer = None
    saved_video_resolution = None
    ys = None
    resolution = None
    temp_title = None

    if url is not None:
        if is_youtube_url(url):
            video_id = youtube_helper.get_youtube_video_id(url)
            temp_title = read_video_title(video_id)

            if PROCESS_SHUN_ONLY and temp_title is not None and "舜" not in temp_title:
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

        saved_video_resolution = -1
        if "youtube" in url:
            saved_video_resolution = get_saved_video_resolution(video_id, url)

        resolution = f"{saved_video_resolution}p"
        ys = None

        if saved_video_resolution == 0:
            # """Video not saved locally, download"""

            ys = youtube_helper.get_stream(url, process_vs_only=process_vs_only)
            resolution = ys.resolution
            vf_analytics.resolution = resolution

            video_folder = f"{config.video_download_folder}"
            if not os.path.exists(video_folder) and not config.process_streamed_videos:
                os.makedirs(video_folder, exist_ok=True)

            video_path = f"{config.video_download_folder}{video_id}.mp4"

            if (
                not os.path.isfile(video_path)
                and not config.process_streamed_videos
                and "youtube" in url
            ):
                try:
                    print(f"\tDownloading video {url} at {resolution}")
                    logger.debug(f"Downloading video {url} at {resolution}")
                    temp_path = youtube_helper.download_video(ys, video_id)

                    if os.path.isfile(temp_path):
                        print(
                            f"Renaming video after download: {temp_path} to {video_path}"
                        )
                        # os.rename(temp_path, video_path)
                        return
                    else:
                        raise Exception(
                            f"{temp_path} not found as expected, cannot rename to {video_path}"
                        )
                    # if resolution != "480p" and resize_video:
                    # ffmpeg.input(temp_path).output(
                    # video_path, vf="scale=854:480"
                    # ).run()
                    # os.remove(temp_path)
                    # else:

                except Exception as e:
                    print(f'error downloading "{url}" ')
                    print(traceback.format_exc())
                    print(ys)
                    print(repr(e))
                    return None
            elif not config.process_streamed_videos:
                print(
                    f"Not downloading because exists: {video_path} and process steram {config.process_streamed_videos}"
                )
        else:
            video_path = f"assets/videos/{video_id}_{resolution}/video.mp4"
            logger.debug(f"found video and loading from {video_path}")

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
            if config.process_streamed_videos and saved_video_resolution == 0:
                # print(f"Processing strem for {ys.url}")
                cap = vf_cv.video_capture_async.VideoCaptureAsync(ys.url)
            elif os.path.isfile(video_path):
                cap = vf_cv.video_capture_async.VideoCaptureAsync(video_path)
            elif os.path.isfile(url):
                cap = vf_cv.video_capture_async.VideoCaptureAsync(url)
            else:
                raise Exception(f"File not found {url}")

            frame_rate = round(cap.get_frame_rate())
            print(f"\t{frame_rate}FPS")
            frame_count = cap.get_frame_count()
            logger.debug(f"{frame_count} at {frame_rate} FPS")
        else:
            cap = cv2.VideoCapture(cam)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            if not cap.isOpened():
                print(f"Failed to open CAM {cam}")
                return

            frame_rate = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            print(f"opened cam {cam} {frame_rate}FPS")
        youtube_video_title = None
        if ys is not None:
            youtube_video_title = ys.title
            save_video_title(video_id, youtube_video_title)
            save_video_url(video_id, resolution, frame_rate, ys.url)
        if ys is not None and PROCESS_SHUN_ONLY and "舜" not in ys.title:
            print("skipping because not shun")
            return True

        if ys is None or ys.title is None:
            youtube_video_title = read_video_title(video_id)

        if cam == -1:
            jpg_folder = f"{config.images_output_folder}{video_id}"
        else:
            time_str = datetime.now().strftime("%Y%m%d%H%M%S")
            jpg_folder = f"{config.images_output_folder}cam{time_str}"

        if not os.path.exists(jpg_folder):
            os.makedirs(jpg_folder, exist_ok=True)

        if saved_video_resolution == 0:
            print(
                f"\tCreating match for youtube video title {ys.title} {frame_rate}FPS "
            )
        else:
            logger.debug(f"\tCreating from saved video")
        match_analyzer = vf_cv.match_analyzer.MatchAnalyzer(
            cap,
            logger,
            jpg_folder=jpg_folder,
            interval=fps,
            frame_rate=frame_rate,
            youtube_video_title=youtube_video_title,
            process_vs_only=process_vs_only,
            config=config,
        )
        processed = 0
        matches_processed = 0
        frames_processed = -1
        while frames_processed != 0:
            print(
                f"\n\n==========================\nProcessing match {match_analyzer.matches_processed}"
            )
            try:
                if config.refresh_replay:
                    WindowController.reload_watch_screen()

                frames_processed = match_analyzer.analyze_next_match(
                    video_id=video_id,
                    cam=cam,
                    frame_count=frame_count,
                    start_frame=processed,
                    obs_helper=obs_helper,
                )  # Extract a frame every 7 seconds

                if config.auto_record:
                    try:
                        time.sleep(5)
                        old_filename = obs_helper.stop_recording()
                        # os.rename(old_filename, match_analyzer.match.get_video_filename())
                        shutil.copy(
                            old_filename, match_analyzer.match.get_video_filename()
                        )
                        os.remove(old_filename)
                    except Exception as e:
                        logger.error("Could not stop recording")
                        logger.error(e)
                        logger.error(traceback.format_exc())

            except vf_cv.PrematureMatchFinishException as e:
                error_message = str(e)
                print(
                    f"\tPremature Match End exception occured {e} processing video {video_id}"
                )
                logger.error(
                    f"Premature match end exception occured {e} processing video {video_id}"
                )
                print_error_csv(
                    match_analyzer.match,
                    resolution,
                    "premature_end",
                    match_number=match_analyzer.matches_processed,
                )
                if STOP_ON_FIRST_ERROR:
                    exit("premature_end")

                match_analyzer.matches_processed = match_analyzer.matches_processed + 1
                continue
            except (
                vf_cv.UnrecognizeTimeDigitException,
                vf_cv.InvalidTimeException,
            ) as e:
                error_message = str(e)
                print(
                    f"Time Error {e} processing video {video_id} match {match_analyzer.matches_processed}"
                )
                logger.error(
                    f"Time Error {e} processing video {video_id} match {match_analyzer.matches_processed}"
                )
                logger.error(traceback.format_exc())

                print_error_csv(
                    match_analyzer.match, resolution, "unrecognized_time_digit"
                )
                if STOP_ON_FIRST_ERROR:
                    exit("unrecognized_time_digit")

                match_analyzer.matches_processed = match_analyzer.matches_processed + 1
                continue
            # except queue.Empty as e:
            # error_message = str(e)
            # print(f"Queue empty {e}")
            # logger.error(f"Queue empty {e}")
            # print_error_csv(match_analyzer.match, resolution, "queue_empty")
            # if STOP_ON_FIRST_ERROR:
            # exit("queue_empty")
            # match_analyzer.matches_processed = match_analyzer.matches_processed + 1
            # continue

            except vf_cv.UnexpectedTimeException as e:
                error_message = str(e)
                print(f"Unexpected time found {e}")
                logger.error(f"Unexpected time found {e}")
                print(traceback.format_exc())
                logger.error(traceback.format_exc())
                print_error_csv(match_analyzer.match, resolution, "unexpected_time")
                if STOP_ON_FIRST_ERROR:
                    exit("unrecognized_time_digit")
                match_analyzer.matches_processed = match_analyzer.matches_processed + 1
                continue

            except vf_cv.UnrecognizeTimeDigitException as e:
                logger.error(f"An exception occured {e} processing video {video_id}")
                print(traceback.format_exc())
                logger.error(traceback.format_exc())
                print(
                    f"UnrecognizedTimeDigit exception occured {e} processing video {video_id}"
                )
                print_error_csv(
                    match_analyzer.match, resolution, "unrecognized_time_digit"
                )
                match_analyzer.matches_processed = match_analyzer.matches_processed + 1
                if STOP_ON_FIRST_ERROR:
                    exit("unrecognized_player_rank")
                continue
            except vf_cv.UnrecognizePlayerRankException as e:
                error_message = str(e)
                logger.error(f"An exception occured {e} processing video {video_id}")
                print(traceback.format_exc())
                logger.error(traceback.format_exc())
                print(
                    f"UnrecognizedPlayerRank exception occured {e} processing video {video_id}"
                )
                print_error_csv(
                    match_analyzer.match, resolution, "unrecognized_player_rank"
                )
                if STOP_ON_FIRST_ERROR:
                    exit("unrecognized_player_rank")
                match_analyzer.matches_processed = match_analyzer.matches_processed + 1
                continue
            except IndexError as e:
                error_message = str(e)
                logger.error(f"An exception occured {e} processing video {video_id}")
                logger.error(repr(e))
                logger.error(traceback.format_exc())
                print(f"IndexError exception occured {e} processing video {video_id}")
                print(traceback.format_exc())
                print(repr(e))
                print_error_csv(match_analyzer.match, resolution, "index_error")
                if STOP_ON_FIRST_ERROR:
                    exit("index_error")
                match_analyzer.matches_processed = match_analyzer.matches_processed + 1
                continue
            if process_vs_only:
                print_csv_match_only(match_analyzer.match)
                processed += frames_processed
                matches_processed += 1
                continue

            if frames_processed != 0 or cam != -1:
                print_csv(match_analyzer.match)
                if config.save_video_snippets:
                    command = match_analyzer.match.to_ffmpeg_copy_command()
                    if command != "":
                        print("\ncommand:")
                        print(match_analyzer.match.to_ffmpeg_copy_command())
                        os.system(match_analyzer.match.to_ffmpeg_copy_command())

                if frames_processed is not None and isinstance(frames_processed, int):
                    processed += frames_processed
                match_analyzer.matches_processed = match_analyzer.matches_processed + 1
                matches_processed += 1

                if FORCE_SINGLE_MATCH_PER_VIDEO:
                    break
    except Exception as e:
        error_message = str(e)
        print(f"\tAnother exception occured {e} processing video {video_id}")
        print(repr(e))
        print(traceback.format_exc())
        logger.error(f"An exception occured {e} processing video {video_id}")
        logger.error(repr(e))
        logger.error(traceback.format_exc())
        if match_analyzer is not None:
            print_error_csv(match_analyzer.match, resolution, "other")
            match_analyzer.matches_processed = match_analyzer.matches_processed + 1
    finally:
        cap.release()
        # if (
        # saved_video_resolution == 0 and FORCE_DELETE_VIDEO or error_message is None
        # ) and os.path.isfile(video_path):
        # os.remove(video_path)

        if (saved_video_resolution == 0 and FORCE_DELETE_VIDEO) and os.path.isfile(
            video_path
        ):
            os.remove(video_path)

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
        repr(e)
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
        with open(title_file) as f:
            s = f.read()
    except:
        s = None

    return s


def save_video_title(video_id, title):
    video_path = f"assets/video_meta/{video_id}/"

    if not os.path.exists(video_path):
        os.makedirs(video_path, exist_ok=True)

    title_file = f"{video_path}{video_id}.title.txt"

    with open(title_file, "w") as f:
        f.write(title)


def save_video_url(video_id, resolution, frame_rate, url):
    video_path = f"assets/video_meta/{video_id}/"

    if not os.path.exists(video_path):
        os.makedirs(video_path, exist_ok=True)

    title_file = f"{video_path}{video_id}_{resolution}_{frame_rate}fps.url.txt"

    with open(title_file, "w") as f:
        f.write(url)


# Main function to run the whole process
def main(
    video_url=None,
    playlists_file=None,
    playlist_file=None,
    process_vs_only=False,
    revo=False,
):

    if revo:
        vf_cv.REVO.capture_window()

    if video_url is not None and "list=" in video_url:
        process_playlist(video_url, process_vs_only)
        return

    if video_url is not None:
        analyze_video(video_url)
        return

    if config.cam_int != -1:
        analyze_video(cam=config.cam_int, url=None)
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
    parser.add_argument(
        "--revo", default=None, help="Set to capture from R.E.V.O. in Windows"
    )
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

    video_folder_param = None
    try:
        video_folder_param = vars(args)["video_folder"]
        if video_folder_param is not None:
            video_folder_param = video_folder_param.strip()
    except:
        video_folder_param = None

    revo = vars(args)["revo"]

    main(
        video_url=video_url,
        playlists_file=playlists_file,
        playlist_file=playlist_file,
        process_vs_only=PROCESS_VS_ONLY,
        revo=revo is not None,
    )
