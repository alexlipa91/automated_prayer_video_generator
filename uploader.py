from simple_youtube_api.Channel import Channel
from simple_youtube_api.LocalVideo import LocalVideo
from google_auth_oauthlib.flow import InstalledAppFlow


class VideoUploader:

    def __init__(self, year, month, day):
        self.year = str(year)
        self.month = str(month).zfill(2)
        self.day = str(day).zfill(2)
        self.folder = "{}{}{}".format(self.year, self.month, self.day)

    def upload(self):
        # flow = InstalledAppFlow.from_client_secrets_file(
        #     "client_secret_956073807168-v9p5sv0267v9jejc8u3uv0od9gvtm0l1.apps.googleusercontent.com.json"
        # )

        channel = Channel()
        channel.login("",
                      "/Users/alessandroliparoti/.config/gcloud/credentials.db")

        print("logged")

        # setting up the video that is going to be uploaded
        video = LocalVideo(file_path="20221118/final_video.mp4")

        # setting snippet
        video.set_title("My Title")
        video.set_description("This is a description")
        video.set_tags(["this", "tag"])
        video.set_category("gaming")
        video.set_default_language("en-US")

        video.set_embeddable(True)
        video.set_privacy_status("public")
        video.set_public_stats_viewable(True)

        video.set_thumbnail_path('test_thumb.png')

        video = channel.upload_video(video)
        print(video.id)
        print(video)


if __name__ == '__main__':
    # VideoUploader(year=2022, month=11, day=18).upload()
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret.json",
        ['https://www.googleapis.com/auth/youtube.upload']
    )
    print(flow.run_local_server().to_json())
