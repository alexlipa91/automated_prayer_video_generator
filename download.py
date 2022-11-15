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
        self.folder = "{}{}{}".format(self.year, self.month, self.day)
        try:
            os.mkdir(self.folder)
        except FileExistsError:
            pass
        self.audio_path = None
        self.audio_duration = 0

    def download_audio(self):
        url = "https://www.vaticannews.va/it/vangelo-del-giorno-e-parola-del-giorno/{}/{}/{}.html"\
            .format(self.year, self.month, self.day)
        print(url)
        req = requests.get(url)
        soup = BeautifulSoup(req.content, "html.parser")
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
                                            locale='it-IT', size='small', color='',
                                            page=1, per_page=n)
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

                metadata["duration"] = \
                    mp.VideoFileClip("{}/{}.mp4".format(self.folder, id)).duration

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
        existing_clips = [VideoFileClip(f) for f in glob.glob("{}/*.mp4".format(self.folder))]

        clips_to_concatenate = []
        total_duration = 0

        while total_duration < self.audio_duration:
            for c in existing_clips:
                clips_to_concatenate.append(c)
                total_duration = total_duration + c.duration
                if total_duration > self.audio_duration:
                    pass

        concatenated = concatenate_videoclips(clips_to_concatenate, method="compose")

        audio = mp.AudioFileClip(self.audio_path)

        with_audio = concatenated.set_audio(audio)
        final_clip = with_audio.subclip(0, audio.duration)

        final_clip.write_videofile("{}/final_video.mp4".format(self.folder))

    def compute_audio_duration(self, file_name):
        audio = MP3(file_name)
        a = audio.info.length
        print("audio length is {}".format(a))
        self.audio_duration = a

    def run(self):
        self.download_audio()

        self.compute_audio_duration(self.audio_path)
        cut_at_seconds = 10

        n_videos_to_download = int(self.audio_duration / cut_at_seconds) + 1

        # download
        videos_and_metadata = self.download_videos(n_videos_to_download)

        # cut length and resize
        for id in videos_and_metadata:
            self.edit_video(id)

        self.create_final_video()

    @staticmethod
    def refresh_video_ids():
        pexel = Pexels('563492ad6f917000010000016686df7bb84c4d249e89acbc3d0adcd4')
        v_ids = []
        for i in range(1, 10):
            search_videos = pexel.search_videos(query='church', orientation='landscape',
                                                locale='', size='small', color='',
                                                page=i, per_page=80)
            for v in search_videos["videos"]:
                v_ids.append([v["id"]])

        import csv
        file = open('videos.csv', 'w+',)
        with file:
            write = csv.writer(file)
            write.writerows(v_ids)


if __name__ == '__main__':
    VideoBuilder.refresh_video_ids()
