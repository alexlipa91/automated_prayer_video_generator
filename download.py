import glob
import os

import requests as requests
from pexelsapi.pexels import Pexels
from mutagen.mp3 import MP3
import moviepy.editor as mp
from moviepy.editor import VideoFileClip, concatenate_videoclips
from bs4 import BeautifulSoup


class VideoBuilder:

    def __init__(self, year, month, day):
        self.year = str(year)
        self.month = str(month).zfill(2)
        self.day = str(day).zfill(2)
        self.folder = "{}{}{}".format(str(year), str(month), str(day))
        try:
            os.mkdir(self.folder)
        except FileExistsError:
            pass
        self.audio_path = None

    def download_audio(self):
        url = "https://www.vaticannews.va/it/vangelo-del-giorno-e-parola-del-giorno/{}/{}/{}.html"\
            .format(self.year, self.month, self.day)
        print(url)
        req = requests.get(url)
        soup = BeautifulSoup(req.content, "html.parser")
        print(soup)
        src = None
        for m in soup.findAll('audio'):
            src = m.get("src", None)
            if src:
                break
        if not src:
            raise Exception("Not able to parse source to get audio url")

        doc = requests.get(src)
        self.audio_path = "{}/{}".format(self.folder, "audio.mp3")
        with open(self.audio_path, 'wb') as f:
            f.write(doc.content)

    def download_videos(self, n=10):
        print("downloading {} videos".format(n))
        pexel = Pexels('563492ad6f917000010000016686df7bb84c4d249e89acbc3d0adcd4')
        search_videos = pexel.search_videos(query='church', orientation='landscape',
                                            size='small', color='', locale='', page=1,
                                            per_page=n)
        ids = {}
        for v in search_videos['videos']:
            file = [x for x in v["video_files"] if x["quality"] == "sd"][0]
            metadata = {"width": file["width"], "height": file["height"]}

            data_url = file["link"]
            id = str(v["id"])

            r = requests.get(data_url)
            with open("{}/{}.mp4".format(self.folder, id), 'wb') as outfile:
                outfile.write(r.content)
                print("saved video {}".format(id))
                ids[id] = metadata
        return ids

    def edit_video(self, id, length=10, width=960, height=540):
        video = VideoFileClip("{}/{}.mp4".format(self.folder, id))
        cut_video = video.subclip(0, min(video.duration, length))
        resized_video = cut_video.resize(width=width, height=height)

        resized_video.write_videofile("{}/{}_edited.mp4".format(self.folder, id))
        print("saved edited video " + id)

        os.remove("{}/{}.mp4".format(self.folder, id))

    def create_final_video(self):
        clips = [VideoFileClip(f) for f in glob.glob("{}/*.mp4".format(self.folder))]
        concatenated = concatenate_videoclips(clips, method="compose")

        audio = mp.AudioFileClip(self.audio_path)
        with_audio = concatenated.set_audio(audio)
        final_clip = with_audio.subclip(0, audio.duration)

        final_clip.write_videofile("{}/final_video.mp4".format(self.folder))

    @staticmethod
    def get_audio_length(file_name):
        audio = MP3(file_name)
        a = audio.info.length
        print("audio length is {}".format(a))
        return a

    def run(self):
        self.download_audio()
        audio_length = VideoBuilder.get_audio_length(self.audio_path)

        cut_at_seconds = 10
        n_videos = int(audio_length / cut_at_seconds) + 1

        # download
        videos_and_metadata = self.download_videos(n_videos)

        # cut length and resize
        for id in videos_and_metadata:
            self.edit_video(id)

        self.create_final_video()


if __name__ == '__main__':
    VideoBuilder(year=2022, month=11, day=1).run()