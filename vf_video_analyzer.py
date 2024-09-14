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
import vf_analytics
import vf_data.match
import youtube_helper
import vf_data


DONT_SAVE = False
SAVE_PIC_ALL = False
DELETE_VIDEO = True

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="vf_match_analyzer.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
)

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


def analyze_video(url, cam=-1):
    start = timer()
    p = pathlib.Path("match_data.csv")
    if not p.is_file():
        with open("match_data.csv", "a") as the_file:
            the_file.write(
                "vid_id,match_id,frame,stage,player1ringname,player1rank,player1character,player2ringname,player2rank,player2character,round_num,player1_rounds_won,p1ko,p1ro,p1ex,player2_rounds_won,p2ko,p2ro,p2ex,time_remaining,youtube_url\n"
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

    start = timer()

    vf_analytics.resolution = "480p"
    resolution = "480p"

    fps = 0.05
    frame_rate = None
    frame_count = None

    processed = 0
    matches_processed = 0

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

        print("Extracting frames")
        match_analyzer = vf_cv.match_analyzer.MatchAnalyzer(
            cap, logger, jpg_folder=jpg_folder, interval=fps, frame_rate=frame_rate
        )
        processed = 0
        matches_processed = 0
        frames_processed = -1
        while frames_processed != 0:
            print(f"\n========\nProcessing match {matches_processed+1}")
            frames_processed = match_analyzer.analyze_next_match(
                video_id=video_id,
                cam=cam,
                frame_count=frame_count,
                start_frame=processed,
            )  # Extract a frame every 7 seconds

            if frames_processed != 0:
                print_csv(match_analyzer.match)
                processed += frames_processed
                matches_processed += 1

    except Exception as e:
        print("error occured")
        logger.error(f"An exception occured {e} processing video {video_id}")
        logger.error(repr(e))
        logger.error(traceback.format_exc())

        if video_path is not None and os.path.isfile(video_path):
            os.remove(video_path)
    finally:
        if (
            matches_processed == 0
            and video_path is not None
            and os.path.isfile(video_path)
        ):
            logger.error(f"removing {video_path} since didn't process matches")
            os.remove(video_path)
        cap.release()
        if DELETE_VIDEO and os.path.isfile(video_path):
            os.remove(video_path)

    elapsed_time = timer() - start  # in seconds
    fps = processed / elapsed_time
    mps = 0
    if matches_processed != 0:
        mps = elapsed_time / matches_processed

    logger.info(
        f"{elapsed_time} seconds to run  {fps} FPS ----- {mps} seconds per match   {matches_processed} matches finished"
    )
    print(
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
