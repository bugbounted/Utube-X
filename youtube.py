import os
import google_auth_oauthlib.flow
import google.oauth2.credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


class YouTubeUploader:
    def __init__(self, client_id, client_secret, access_token, refresh_token, video_title, video_description,
                 video_category_id, privacy_status):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.video_title = video_title
        self.video_description = video_description
        self.video_category_id = video_category_id
        self.privacy_status = privacy_status

        self.youtube = self.build_youtube_client()

    def build_youtube_client(self):
        credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(info=self.get_credentials(),
                                                                                     scopes=['https://www.googleapis.com/auth/youtube.upload',
                                                                                             'https://www.googleapis.com/auth/youtube.force-ssl'])
        return build('youtube', 'v3', credentials=credentials)

    def get_credentials(self):
        return {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'token_uri': 'https://oauth2.googleapis.com/token',
        }

    def upload_video(self, file_path):
        try:
            # create a MediaFileUpload object for the video file
            media = MediaFileUpload(file_path)

            # build the request body for the video metadata
            body = {
                'snippet': {
                    'title': self.video_title,
                    'description': self.video_description,
                    'categoryId': self.video_category_id
                },
                'status': {
                    'privacyStatus': self.privacy_status
                }
            }

            # execute the YouTube API request to upload the video
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            response = request.execute()

            # return the video ID of the uploaded video
            return response.get('id')

        except HttpError as e:
            print(f'An HTTP error {e.resp.status} occurred: {e.content}')
            return None
