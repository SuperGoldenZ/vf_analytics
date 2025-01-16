import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube']

def authenticate_youtube():
    """Authenticate and return the YouTube API service."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)

def upload_video(youtube, file_path, playlist_id, videos):
    """Uploads a video to YouTube and adds it to a playlist."""
    file_name = os.path.basename(file_path)
    title = os.path.splitext(file_name)[0]  # Title from filename
    #title = title.replace("(", "(")
    #title = title.replace(")", "]")
    #title = title.replace("\"", "'")
    title = title.replace("R.E.V.O.", "REVO")
    title = title.replace("Lv. ", "Lv.")
    if (len(title) > 100):
        title = title.replace(" - ", "-")

    # Check if the video already exists
    if video_exists(title, videos):
        return  # Skip upload if the video exists

    description = "Ranked Match from the Open Beta"

    # Prepare the request body
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["Virtua Fighter 5 R.E.V.O.", "Gameplay", "Virtua Fighter"],
            "categoryId": "20",  # Category: Gaming
        },
        "status": {            
            "privacyStatus": "unlisted",  # Change to "unlisted" or "private" if needed
            "selfDeclaredMadeForKids": False
        },
    }


    try:
        print(f"Uploading video title {title}")
        print(f"Title length: {len(title)} characters")

        # Upload the video
        request = youtube.videos().insert(
            part="snippet,status,recordingDetails",
            body=body,
            media_body=file_path
        )
        response = request.execute()

        print(f"Uploaded: {title}")
        video_id = response['id']

        # Add to playlist
        if playlist_id:
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        },
                        "categoryId": "20"
                    }
                }
            ).execute()
            print(f"Added to playlist: {playlist_id}")
    except HttpError as e:
        print(f"An error occurred: {e}")
        return None

def get_uploaded_videos(youtube):
    """Retrieve all videos uploaded to the authenticated YouTube account."""
    videos = []
    request = youtube.search().list(
        part="snippet",
        forMine=True,
        type="video",
        maxResults=50  # Retrieve up to 50 videos per request
    )
    while request:
        response = request.execute()
        videos.extend(response.get("items", []))
        request = youtube.search().list_next(request, response)
    return videos

def video_exists(title, videos):
    for video in videos:
        if video["snippet"]["title"] == title:
            print(f"Video with title '{title}' already exists. Skipping upload.")
            return True
    return False

def main():
    # Authenticate to YouTube
    youtube = authenticate_youtube()

    # Configuration
    folder_path = "/mnt/sdb/Users/alexa/Videos/2024Q4 Open Beta/Matches/"  # Replace with your folder path
    playlist_id = "PL2Ooeuwh6wzmpQiE8V2S_pWf_W0T_TJlI"  # Replace with your playlist ID
    
    #recording_date = "2023-12-01T00:00:00.000Z"  # Replace with the recording date in ISO format

    """Check if a video with the given title exists on the channel."""
    videos = get_uploaded_videos(youtube)

    # Process all video files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            file_path = os.path.join(folder_path, file_name)

            try:
                upload_video(youtube, file_path, playlist_id, videos)
            except Exception as e:
                print(f"Error while uploading video {file_path} {e}")
            
if __name__ == "__main__":
    main()
