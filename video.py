import datetime
import glob
import locale
import os

import requests as requests
from pexelsapi.pexels import Pexels
import moviepy.editor as mp
from moviepy.video.VideoClip import TextClip
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
import random
from mutagen.mp3 import MP3


class VideoDownloader:

    def __init__(self, year, month, day):
        self.year = str(year)
        self.month = str(month).zfill(2)
        self.day = str(day).zfill(2)
        self.folder = "{}{}{}".format(self.year, self.month, self.day)

        self.videos = open('videos.csv', 'r').readlines()
        random.shuffle(self.videos)

        self.audio_duration = MP3("{}/vangelo.mp3".format(self.folder)).info.length

        self.index = 0
        self.duration = 0

        try:
            os.mkdir(self.folder)
        except FileExistsError:
            pass

    def download_video(self, cut_at_seconds=10):
        print("downloading video {}".format(self.index))
        url = self.videos[self.index]
        print("url {}".format(url))
        r = requests.get(url)

        file_name = "{}/video_{}.mp4".format(self.folder, self.index)
        tmp_file_name = file_name + ".tmp"

        with open(tmp_file_name, 'wb') as outfile:
            outfile.write(r.content)

        self.index = self.index + 1
        if self.index > len(self.videos):
            self.index = 0

        # edit
        video = VideoFileClip(tmp_file_name)
        # cut
        get_first = min(video.duration, cut_at_seconds)
        cut_video = video.subclip(0, get_first)
        self.duration = self.duration + get_first
        # resize
        resized_video = cut_video.resize(width=960, height=540)

        resized_video.write_videofile(file_name)

        os.remove(tmp_file_name)
        print("video file saved {}".format(file_name))

    def run(self):
        while self.duration < self.audio_duration:
            print("missing duration: {}".format(self.audio_duration - self.duration))
            try:
                self.download_video()
            except Exception:
                print("failed")

    @staticmethod
    def refresh_video_ids():
        pexel = Pexels('563492ad6f917000010000016686df7bb84c4d249e89acbc3d0adcd4')
        v_ids = []
        for i in range(1, 20):
            search_videos = pexel.search_videos(query='church', orientation='landscape',
                                                locale='', size='small', color='',
                                                page=i, per_page=80)
            for v in search_videos["videos"]:
                file = [x for x in v["video_files"] if x["quality"] == "sd"][0]
                v_ids.append([file["link"]])

        import csv
        file = open('videos.csv', 'w+',)
        with file:
            write = csv.writer(file)
            write.writerows(v_ids)


class VideoComposer:

    def __init__(self, year, month, day):
        self.year = str(year)
        self.month = str(month).zfill(2)
        self.day = str(day).zfill(2)

        self.date = datetime.datetime(year=year, month=month, day=day)
        self.folder = "{}{}{}".format(self.year, self.month, self.day)

        self.total_duration = MP3("{}/vangelo.mp3".format(self.folder)).info.length

    def get_santo_del_giorno(self):
        # todo finish
        s = requests\
            .get("https://www.santodelgiorno.it/santi.json?data={}-{}-{}".format(self.year, self.month, self.day))\
            .json()
        for x in s:
            print(x["nome"])

    def preview(self):
        from PIL import ImageDraw, Image, ImageFont

        img = Image.open('resources/bible.jpeg')
        final_img = ImageDraw.Draw(img)
        locale.setlocale(locale.LC_ALL, 'it_IT')
        w, h = img.size
        font = ImageFont.truetype("resources/Tahoma_Regular_font.ttf", 195)
        final_img.text((w/2, h/3), "Letture del Giorno\n\n\n\n{}".format(self.date.strftime("%d %B %Y")),
                       fill=(255, 255, 255), align="center", anchor="ms", font=font)
        img.save("{}/preview.jpeg".format(self.folder))

    def run(self):
        clips = [VideoFileClip(f) for f in glob.glob("{}/video_*.mp4".format(self.folder))]

        concatenated = concatenate_videoclips(clips, method="compose")

        audio = mp.AudioFileClip("{}/vangelo.mp3".format(self.folder))

        final_clip = self\
            .add_subs(concatenated.set_audio(audio))\
            .subclip(0, audio.duration)

        final_clip.write_videofile("{}/final_video.mp4".format(self.folder))

    def add_subs(self, video_clip):
        subtitles = SubtitlesClip("{}/vangelo.srt".format(self.folder),
                                  lambda txt: TextClip(txt,
                                                       font='Tahoma-bold',
                                                       method="caption",
                                                       size=video_clip.size,
                                                       fontsize=48,
                                                       stroke_color="black",
                                                       stroke_width=2,
                                                       # transparent=False,
                                                       color='white')) \
            .set_pos('center')
        return CompositeVideoClip([video_clip, subtitles])


if __name__ == '__main__':
    # todo youtube uploader
    # vd = VideoDownloader(year=2022, month=11, day=18)
    # vd.run()

    v = VideoComposer(year=2022, month=11, day=18, total_duration=221)
    # v.get_santo_del_giorno()
    # v.preview()
    v.run()

    # v.add_subs(VideoFileClip("20221118/video_2.mp4")).write_videofile("test.mp4")
