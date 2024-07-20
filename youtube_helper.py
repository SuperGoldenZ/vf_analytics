from pytube import YouTube
from pytube import Playlist
from urllib.parse import urlparse, parse_qs
import os

RESOLUTION_720P='720p'
RESOLUTION_360P='360p'

playlists=[
    #Jacky
     "https://www.youtube.com/playlist?list=PLNbC0SRw-xBfYSZQ8xdcaFRzPZAdUdGLv"
    #Akira
    ,"https://www.youtube.com/playlist?list=PLNbC0SRw-xBeYys2x49se6u7C-Uyx9zuJ"
    #Blaze
    ,"https://www.youtube.com/playlist?list=PLNbC0SRw-xBfAJ80HDNCSp1OTrfgUH11K"
    #Shun
    ,"https://www.youtube.com/playlist?list=PLNbC0SRw-xBdeiiO3OkwlxHpwETQU-irP"
    #Brad
    ,"https://www.youtube.com/playlist?list=PLNbC0SRw-xBetzQbU72GsYT4d9mn1LCEn"
    #Eileen
    ,"https://www.youtube.com/playlist?list=PLNbC0SRw-xBcDIo2JwMkxhaVayDGeDiCg"
    #Jeffrey
    ,"https://www.youtube.com/playlist?list=PLNbC0SRw-xBd1PALdKnj5hGx5HFM4-AQe"
    #Taka
    ,"https://www.youtube.com/playlist?list=PLNbC0SRw-xBen06zc2hbkZuaz9JdW4weF"
    #Goh
    ,"https://www.youtube.com/playlist?list=PLNbC0SRw-xBcWX8I6I49Rch1xDcZRaUGe"
    #Jean
    ,"https://www.youtube.com/playlist?list=PLNbC0SRw-xBeZaLqzgehiwSqFlVcLzhU3"
    #Lau
    ,"https://www.youtube.com/playlist?list=PLNbC0SRw-xBei5K68iaf9_7TzbLNGmjax"
    #Lion
    ,"https://www.youtube.com/playlist?list=PLNbC0SRw-xBfiwY36cpygqXUtWEHWgt1N"
    #Lei Fei
    ,"https://www.youtube.com/playlist?list=PLNbC0SRw-xBdhp8Oon9JBVT1ay1Ek5RaN"
    #Wolf
    ,"https://www.youtube.com/playlist?list=PLNbC0SRw-xBf-yVzkQY4b60dBFGwcIFsc"
    #Aoi
    ,"https://www.youtube.com/playlist?list=PLNbC0SRw-xBdcg-2FWVgkNeuzUrnVJMTt"
    #Pai
    ,"https://www.youtube.com/playlist?list=PLNbC0SRw-xBdEpGLSg2hKoo_8s2WWWNC5"
    #Sarah
    ,"https://www.youtube.com/playlist?list=PLNbC0SRw-xBcYW_O5rwDpmW1zUfkSP9KX"
    #Kage
    ,"https://www.youtube.com/playlist?list=PLNbC0SRw-xBcFgC5wim7NDPNK1p_xYTIh"
    #Vanessa
    ,"https://www.youtube.com/playlist?list=PLNbC0SRw-xBdAJ815ZfAvi267Vme32izX"
    ]

play_collection = [
    #Jean
     "https://www.youtube.com/playlist?list=PLIYqlJQujs8ZtpySzu1F_bAmziU8Uu98V"

    #Eileen
    ,"https://www.youtube.com/playlist?list=PLIYqlJQujs8ZSURKjVUIakj2qwCbg63UJ"

    #Brad
    ,"https://www.youtube.com/playlist?list=PLIYqlJQujs8Z1GhS-qFvbO3ayRlPDGmNT"

    #Goh
    ,"https://www.youtube.com/playlist?list=PLIYqlJQujs8bTtru5AvEvD6-ICzVvmvgK"

    #Vanessa
    ,"https://www.youtube.com/playlist?list=PLIYqlJQujs8av2XTJufdPZwtEzYVnNsX3"

    # Lei Fei
    ,"https://www.youtube.com/playlist?list=PLIYqlJQujs8ZbKhycf5UAZkub8mg1qFQ9"

    # Aoi
    ,"https://www.youtube.com/playlist?list=PLIYqlJQujs8Yz9sZsXxirFN269eFRZMWP"

    #Lion
    ,"https://www.youtube.com/playlist?list=PLIYqlJQujs8b4SD2VPsuCV5SjpY5ts5Qm"

    #Shun
    ,"https://www.youtube.com/playlist?list=PLIYqlJQujs8Z7pt59hcla30lF2nWaliOa"

    #Jacky
    ,"https://www.youtube.com/playlist?list=PLIYqlJQujs8Zs8q4bFYsUdg-uibVBzMRv"

    #Sarah
    ,"https://www.youtube.com/playlist?list=PLIYqlJQujs8beSzE6jmPYJD-vZ6TKuIMF"

    #Kage
    ,"https://www.youtube.com/playlist?list=PLIYqlJQujs8YosuB6sViwjiD4XT9wO1ZA"

    #Jeffry
    ,"https://www.youtube.com/playlist?list=PLIYqlJQujs8bX7F2hkmsZTf-B17aNONP-"

    #Wolf
    ,"https://www.youtube.com/playlist?list=PLIYqlJQujs8asXTd7jGgVYj7rwSYqOqa5"

    #Pai Chan
    ,"https://www.youtube.com/playlist?list=PLIYqlJQujs8YqEM4f_ruR4cpkSaNHLjSD"

    #Akira
    ,"https://www.youtube.com/playlist?list=PLIYqlJQujs8ZXBM9_oDrRoWJx1X0ADqUL"

    #Lau Chan
    ,"https://www.youtube.com/playlist?list=PLIYqlJQujs8aLQJNpYv5xTFiF567jqrOG"

    #Taka
    ,"https://www.youtube.com/playlist?list=PLIYqlJQujs8Yd6cY67kca33xEeAE19RJd"

    #El Blaze 2
    ,"https://www.youtube.com/playlist?list=PLIYqlJQujs8YRfPjQuHcjVbffN46jiOsY"
]

playlists_streamer = [
    #Panchan
     "https://www.youtube.com/playlist?list=PLVbGvjJ7wGuGfLBtd0vvLbrLHSSUu9gK1"

    #Ami Usagi
    ,"https://www.youtube.com/playlist?list=amiusagi"
]


#panchan_videos = [
#]

def get_stream(url, resolution="480p"):
    yt = YouTube(url, use_oauth=True)
    fps = 30
    if (resolution=="720p"):
        fps=30

    try:
        ys = yt.streams.filter(res=resolution, fps=fps).first()
        if (ys is None and resolution == "480p"):
            return get_stream(url, '720p')
        return ys
    except:
        if (resolution == '480p'):
            print("no 480p so trying 720p")
            return get_stream(url, '720p')
    raise Exception(f"Resolution not found for {url} {resolution}")

# Step 1: Download the YouTube video
def download_video(ys, vid, resolution="480p"):
    output_path = f"/tmp/{vid}.mp4"

    ys.download(filename=output_path)
    return output_path

def get_youtube_video_id(url):
    # Parse the URL
    parsed_url = urlparse(url)

    # Extract the query parameters
    query_params = parse_qs(parsed_url.query)

    # Get the value of the 'v' parameter
    return query_params.get('v', [None])[0]


def get_video_urls_from_playlist(playlist):
    urls=[]

    print(f"Processing  playlist {playlist}")
    parsed_url = urlparse(playlist)

    # Extract the query parameters
    query_params = parse_qs(parsed_url.query)

    # Get the value of the 'v' parameter
    playlist_id = query_params.get('list', [None])[0]

    if (os.path.isfile(f"playlist-{playlist_id}")):
        print(f"reading from playlist file playlist-{playlist_id}")
        with open (f"assets/playlist-{playlist_id}") as fp:
            for line in fp:
                urls.append(line.strip())
        return urls

    playlist_urls = Playlist(playlist)

    for url in playlist_urls:
        urls.append(url)

    with open(f"assets/playlist-{playlist_id}", 'w') as f:
        print(f"saving to playlist file playlist-{playlist_id}")
        for url in urls:
            f.write(f"{url}\n")


    return urls

