"""YouTube API servlet using google-api-python-client.

This replaces the deprecated gdata library.
"""

import logging

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from dancedeets import app
from dancedeets import base_servlet
from dancedeets import keys

# YouTube API settings
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


def get_youtube_service():
    """Build and return a YouTube API service object."""
    api_key = keys.get('google_server_key')
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=api_key)


@app.route('/youtube_simple_api')
class YoutubeSimpleApiHandler(base_servlet.BareBaseRequestHandler):
    def get(self):
        action = self.request.get('action')
        youtube = get_youtube_service()

        try:
            if action == 'favorites':
                # Note: YouTube API v3 doesn't have a direct favorites endpoint
                # You would need to get the user's "liked videos" playlist
                username = self.request.get('username')
                text_query = self.request.get('query')

                # Get channel ID from username
                channels_response = youtube.channels().list(
                    forUsername=username,
                    part='contentDetails'
                ).execute()

                if not channels_response.get('items'):
                    self.response.out.write('Channel not found')
                    return

                # Get likes playlist
                uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists'].get('likes')
                if not uploads_playlist_id:
                    self.response.out.write('No likes playlist found')
                    return

                # Get videos from playlist
                playlist_response = youtube.playlistItems().list(
                    playlistId=uploads_playlist_id,
                    part='snippet',
                    maxResults=50
                ).execute()

                print('\n\n')
                for item in playlist_response.get('items', []):
                    print('Video title: %s' % item['snippet']['title'])

            elif action == 'playlists':
                username = self.request.get('username')
                text_query = self.request.get('query')

                # Get channel ID from username
                channels_response = youtube.channels().list(
                    forUsername=username,
                    part='id'
                ).execute()

                if not channels_response.get('items'):
                    self.response.out.write('Channel not found')
                    return

                channel_id = channels_response['items'][0]['id']

                # Get playlists for channel
                playlists_response = youtube.playlists().list(
                    channelId=channel_id,
                    part='snippet',
                    maxResults=50
                ).execute()

                print('\n\n')
                for item in playlists_response.get('items', []):
                    print('Playlist title: %s: %s' % (item['id'], item['snippet']['title']))

            elif action == 'one_playlist':
                username = self.request.get('username')
                text_query = self.request.get('query')
                playlist_id = self.request.get('playlist_id')

                # Get videos from specific playlist
                playlist_response = youtube.playlistItems().list(
                    playlistId=playlist_id,
                    part='snippet',
                    maxResults=50
                ).execute()

                print('\n\n')
                for item in playlist_response.get('items', []):
                    print('Video title: %s' % item['snippet']['title'])

            elif action == 'search':
                text_query = self.request.get('query')

                # Search for videos
                search_response = youtube.search().list(
                    q=text_query,
                    part='snippet',
                    type='video',
                    maxResults=50
                ).execute()

                print('\n\n')
                for item in search_response.get('items', []):
                    print('Video title: %s' % item['snippet']['title'])

            else:
                self.response.out.write('Unknown action: %s' % action)

        except HttpError as e:
            logging.error('YouTube API error: %s', e)
            self.response.out.write('YouTube API error: %s' % e)
