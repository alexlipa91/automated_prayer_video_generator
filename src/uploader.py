#!/usr/bin/python
'''Uploads a video to YouTube.'''

# Nono Martínez Alonso
# youtube.com/@NonoMartinezAlonso
# https://github.com/youtube/api-samples/blob/master/python/upload_video.py

import datetime
import io
from http import client
import httplib2
import random
import time


from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow


# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, client.NotConnected,
                        client.IncompleteRead, client.ImproperConnectionState,
                        client.CannotSendRequest, client.CannotSendHeader,
                        client.ResponseNotReady, client.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = '../client_secret.json'

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube',
          'https://www.googleapis.com/auth/youtubepartner']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')


def generate_credentials_file():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES
    )
    credentials = flow.run_local_server(port=8080)
    with open("../credentials.json", "w") as outfile:
        outfile.write(credentials.to_json())


# Authorize the request and store authorization credentials.
def get_authenticated_service():
    # flow = InstalledAppFlow.from_client_secrets_file(
    #     CLIENT_SECRETS_FILE, SCOPES
    # )
    credentials = Credentials.from_authorized_user_file("../credentials.json")
    # credentials = flow.run_local_server(port=8080)
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def initialize_upload(youtube, file, thumbnail, title, description, category, tags, privacy_status):
    body = dict(
        snippet=dict(
            title=title,
            description=description,
            tags=tags,
            categoryId=category,
            thumbnails=dict(
                default=dict(
                    url=thumbnail
                )
            )
        ),
        status=dict(
            selfDeclaredMadeForKids=False,
            privacyStatus=privacy_status
        )
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        # The chunksize parameter specifies the size of each chunk of data, in
        # bytes, that will be uploaded at a time. Set a higher value for
        # reliable connections as fewer chunks lead to faster uploads. Set a lower
        # value for better recovery on less reliable connections.
        #
        # Setting 'chunksize' equal to -1 in the code below means that the entire
        # file will be uploaded in a single HTTP request. (If the upload fails,
        # it will still be retried where it left off.) This is usually a best
        # practice, but if you're using Python older than 2.6 or if you're
        # running on App Engine, you should set the chunksize to something like
        # 1024 * 1024 (1 megabyte).
        media_body=MediaFileUpload(file, chunksize=-1, resumable=True)
    )

    return resumable_upload(insert_request)

# This method implements an exponential backoff strategy to resume a
# failed upload.


def resumable_upload(request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print('Uploading file...')
            status, response = request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print('Video id "%s" was successfully uploaded.' %
                          response['id'])
                else:
                    exit('The upload failed with an unexpected response: %s' % response)
        except (HttpError, e):
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = 'A retriable HTTP error %d occurred:\n%s' % (e.resp.status,
                                                                     e.content)
            else:
                raise
        except (RETRIABLE_EXCEPTIONS, e):
            error = 'A retriable error occurred: %s' % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit('No longer attempting to retry.')

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print('Sleeping %f seconds and then retrying...' % sleep_seconds)
            time.sleep(sleep_seconds)
    if response:
        return response['id']


def set_thumbnail(youtube, video_id, thumbnail_file):
    request = youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(thumbnail_file)
    )
    response = request.execute()
    print(response)


def add_to_playlist(youtube, video_id):
    add_video_request = youtube.playlistItems().insert(
        part="snippet",
        body={
            'snippet': {
                'playlistId': "PLYFkvAawma-XL1-y8nZU3tLf9WTKnI11m",
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': video_id
                }
            }
        }
    )
    response = add_video_request.execute()
    print(response)


def add_transcript(youtube, video_id, transcript_file_path):
    req = youtube.captions().insert(
        part="snippet",
        body=dict(
            snippet=dict(
                videoId=video_id,
                language="it",
                name="Trascrizione",
                isDraft=False
            )
        ),
        media_body=MediaFileUpload(transcript_file_path)
    )
    response = req.execute()
    print(response)


def download_transcript_srt(youtube, caption_id, file_path):
    request = youtube.captions().download(
        id=caption_id,
        tfmt="srt",
    )
    fh = io.FileIO(file_path, "wb")

    download = MediaIoBaseDownload(fh, request)
    complete = False
    while not complete:
        status, complete = download.next_chunk()


def upload(config):
    date_string = datetime.datetime(year=int(config.year),
                                    month=int(config.month),
                                    day=int(config.day)).strftime("%d %B %Y")
    file = "{}/final_video.mp4".format(config.folder)
    source_url = "https://www.vaticannews.va/it/vangelo-del-giorno-e-parola-del-giorno/{}/{}/{}.html"\
        .format(config.year, config.month, config.day)
    thumbnail = "{}/preview.jpeg".format(config.folder)
    title = "Vangelo del Giorno: {}".format(date_string)
    description = "Vangelo e letture del giorno, con commento del Santo Padre\n\nOfferto da: {}".format(source_url)
    category = "22"
    tags = ["vangelo", "preghiere", "chiesa", "gesù", "bibbia", "vaticano", "papa"]
    privacy_status = "public"

    youtube = get_authenticated_service()
    video_id = initialize_upload(youtube, file, thumbnail, title, description, category, tags, privacy_status)
    set_thumbnail(youtube, video_id, "{}/preview.jpeg".format(config.folder))
    add_to_playlist(youtube, video_id)
    add_transcript(youtube, video_id, "{}/transcript.txt".format(config.folder))


if __name__ == '__main__':
    import json
    # generate_credentials_file()
    # sys.exit(1)
    # os.environ["CREDENTIALS_FILE"] = "credentials.json"

    y = get_authenticated_service()
    # req = y.captions().list(
    #     part="snippet",
    #     videoId="Cq3mE4V3DGw"
    # )
    # s = json.dumps(req.execute())
    # print(s)

    # add_transcript(y, "Cq3mE4V3DGw", "20221126/transcript.txt")

    # download_transcript_srt(y, "AUieDabTop6Xj678ENZojEnEpQUptwD-tCxem8xUW-OMSlTQnznKZ7YmY2x4XMg",
    #                         "20221126/downloaded_transcript.srt")
