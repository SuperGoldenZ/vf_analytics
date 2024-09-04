from urllib.parse import urlparse, parse_qs
import os
import logging
import traceback

from pytubefix import YouTube
from pytubefix import Playlist

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="analyze_youtube.log", encoding="utf-8", level=logging.ERROR
)

RESOLUTION_720P = "720p"
RESOLUTION_360P = "360p"

STREAM_SEARCH = [
    {"resolution": "480p", "fps": 30},
    {"resolution": "480p", "fps": 60},
    {"resolution": "720p", "fps": 30},
    {"resolution": "720p", "fps": 60},
    {"resolution": "1080p", "fps": 30},
    {"resolution": "1080p", "fps": 60},
]


def get_stream(url, youtube_auth=True):
    yt = YouTube(url, use_oauth=youtube_auth)

    logger.debug(f"made youtube for {url}")
    for stream in yt.streams:
        logger.debug(stream)

    try:
        for stream_params in STREAM_SEARCH:
            for stream in yt.streams:
                logger.debug(f"got stream {stream}")

        ys = yt.streams.filter(
            res=stream_params["resolution"], fps=stream_params["fps"]
        ).first()
        if ys is not None:
            return ys
    except Exception as error:
        logger.error(f"error occured getting stream {error}")
        logger.error(traceback.format_exc())

    raise Exception(f"Not suitable resolution and FPS found for {url}")


# Step 1: Download the YouTube video
def download_video(ys, vid, resolution="480p"):
    output_path = f"assets/videos/{vid}.mp4"

    ys.download(filename=output_path)
    return output_path


def get_youtube_video_id(url):
    # Parse the URL
    parsed_url = urlparse(url)

    # Extract the query parameters
    query_params = parse_qs(parsed_url.query)

    # Get the value of the 'v' parameter
    return query_params.get("v", [None])[0]


def get_video_urls_from_playlist(playlist):
    urls = []

    logger.debug(f"Processing  playlist {playlist}")
    parsed_url = urlparse(playlist)

    # Extract the query parameters
    query_params = parse_qs(parsed_url.query)

    # Get the value of the 'v' parameter
    playlist_id = query_params.get("list", [None])[0]

    if os.path.isfile(f"playlist-{playlist_id}"):
        logger.debug(f"reading from playlist file playlist-{playlist_id}")
        with open(f"assets/playlist-{playlist_id}") as fp:
            for line in fp:
                urls.append(line.strip())
        return urls

    playlist_urls = Playlist(playlist)

    for url in playlist_urls:
        urls.append(url)

    with open(f"assets/playlist-{playlist_id}", "w") as f:
        logger.debug(f"saving to playlist file playlist-{playlist_id}")
        for url in urls:
            f.write(f"{url}\n")

    return urls
