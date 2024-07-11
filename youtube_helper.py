from pytube import YouTube
from pytube import Playlist
from urllib.parse import urlparse, parse_qs
import os

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
    #El Blaze 2
    ,"https://www.youtube.com/playlist?list=PLIYqlJQujs8YRfPjQuHcjVbffN46jiOsY"
    ]

playlists = [
    #Jean
    "https://www.youtube.com/playlist?list=PLIYqlJQujs8ZtpySzu1F_bAmziU8Uu98V"

    #Eileen
    ,"https://www.youtube.com/playlist?list=PLIYqlJQujs8ZSURKjVUIakj2qwCbg63UJ"

    #Brad
    ,"https://www.youtube.com/playlist?list=PLIYqlJQujs8Z1GhS-qFvbO3ayRlPDGmNT"
]

# Step 1: Download the YouTube video
def download_video(url, output_path='video.mp4'):
    print(f"Downloading {url} to {output_path}")
    yt = YouTube(url)
    ys = yt.streams.filter(res='720p').first()
    ys.download(filename=output_path)
    print(f"... done! Downloaded {url} to {output_path}")

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
        with open (f"playlist-{playlist_id}") as fp:
            for line in fp:                    
                urls.append(line.strip())
        return urls

    playlist_urls = Playlist(playlist)

    for url in playlist_urls:
        urls.append(url)

    with open(f"playlist-{playlist_id}", 'w') as f:
        print(f"saving to playlist file playlist-{playlist_id}")
        for url in urls:
            f.write(f"{url}\n")
    
    
    return urls

