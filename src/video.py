import datetime
import glob
import traceback

import requests as requests
from pexelsapi.pexels import Pexels
import moviepy.editor as mp
from moviepy.video.tools.subtitles import SubtitlesClip
import random
from mutagen.mp3 import MP3
from moviepy.editor import *
import csv

WIDTH = 1920
HEIGHT = 1080


class VideoDownloader:

    def __init__(self, config):
        self.config = config

        self.videos = open('resources/videos.csv', 'r').readlines()
        random.shuffle(self.videos)

        self.audio_duration = MP3("{}/vangelo.mp3".format(config.folder)).info.length

        self.index = 0
        self.duration = 0

        try:
            os.mkdir(config.folder)
        except FileExistsError:
            pass

    def download_video(self):
        url = self.videos[self.index]
        r = requests.get(url)

        file_name = "{}/video_{}.mp4".format(self.config.folder, self.index)
        tmp_file_name = file_name + ".tmp"

        with open(tmp_file_name, 'wb') as outfile:
            outfile.write(r.content)

        self.index = self.index + 1
        if self.index > len(self.videos):
            self.index = 0

        # edit
        video = VideoFileClip(tmp_file_name)
        # cut
        get_first = min(video.duration, self.config.video_parts_max_length_seconds)
        cut_video = video.subclip(0, get_first)
        self.duration = self.duration + get_first
        # resize
        resized_video = cut_video.resize(width=WIDTH, height=HEIGHT)

        resized_video.write_videofile(file_name, verbose=False, logger=None)

        os.remove(tmp_file_name)

    def run(self):
        target_duration = self.audio_duration if self.config.duration_seconds is None else self.config.duration_seconds

        while self.duration < target_duration:
            try:
                self.download_video()
            except Exception:
                print("failed video download")
                traceback.print_exc()


def refresh_video_ids(definition="sd", size="small"):
    pexel = Pexels('563492ad6f917000010000016686df7bb84c4d249e89acbc3d0adcd4')
    v_ids = []
    for i in range(1, 20):
        search_videos = pexel.search_videos(query='church', orientation='landscape',
                                            locale='', size=size, color='',
                                            page=i, per_page=80)
        videos = search_videos["videos"]
        for v in videos:
            hd_files = [x for x in v["video_files"] if x["quality"] == definition]
            if len(hd_files) > 0:
                v_ids.append([hd_files[0]["link"]])
            else:
                print("no {} file".format(definition))

    file = open('resources/videos.csv', 'w+', )
    with file:
        write = csv.writer(file)
        write.writerows(v_ids)


class VideoComposer:

    def __init__(self, config):
        self.config = config

    def get_santo_del_giorno(self):
        # todo finish
        s = requests \
            .get("https://www.santodelgiorno.it/santi.json?data={}-{}-{}".format(self.year, self.month, self.day)) \
            .json()
        for x in s:
            print(x["nome"])

    def generate_preview_pope(self):
        from PIL import ImageDraw, Image, ImageFont

        img = Image.open('resources/pope_empty.jpeg')
        final_img = ImageDraw.Draw(img)
        w, h = img.size
        font_main = ImageFont.truetype("resources/Tahoma_Regular_font.ttf", 100)
        font_small = ImageFont.truetype("resources/Tahoma_Regular_font.ttf", 40)

        date = datetime.datetime(year=int(self.config.year), month=int(self.config.month), day=int(self.config.day))

        final_img.text((w / 3, h / 4), "Letture del\nGiorno",
                       fill=(255, 255, 255), align="center", anchor="ms", font=font_main)
        final_img.text((w / 3, h / 1.61), "con commento del\nSanto Padre",
                       fill=(255, 255, 255), align="center", anchor="ms", font=font_small)
        final_img.text((w / 3, h / 1.16), "{}".format(self.get_date_string(date)),
                       fill=(255, 255, 255), align="center", anchor="ms",
                       font=ImageFont.truetype("resources/Tahoma_Regular_font.ttf", 70))

        img.show()
        img.save("{}/preview.jpeg".format(self.config.folder))

    def get_date_string(self, date):
        months = {
            1: "Gennaio",
            2: "Febbraio",
            3: "Marzo",
            4: "Aprile",
            5: "Maggio",
            6: "Giugno",
            7: "Luglio",
            8: "Agosto",
            9: "Settembre",
            10: "Ottobre",
            11: "Novembre",
            12: "Dicembre"
        }
        return "{} {} {}".format(date.day, months[date.month], date.year)

    def run(self):
        print("composing video")
        subscribe_prompt_duration = 3

        clips = [VideoFileClip(f) for f in glob.glob("{}/video_*.mp4".format(self.config.folder))]
        print("concatenating {} videos".format(len(clips)))

        concatenated = concatenate_videoclips(clips, method="compose").set_start(subscribe_prompt_duration)

        audio = CompositeAudioClip([mp.AudioFileClip("{}/vangelo.mp3".format(self.config.folder))
                                   .set_start(subscribe_prompt_duration)])
        if self.config.duration_seconds:
            audio = audio.set_duration(self.config.duration_seconds)

        print("audio duration {}".format(audio.duration))

        subscribe_image = ImageClip("resources/pope_subscribe.jpeg").set_start(0) \
            .set_duration(subscribe_prompt_duration)\
            # .resize(1920, 1082)

        print("subscribe image built")

        composite = CompositeVideoClip([concatenated, subscribe_image]).set_audio(audio)

        print("composed")

        composite \
            .subclip(0, audio.duration) \
            .write_videofile("{}/final_video.mp4".format(self.config.folder),
                             verbose=False, logger=None)

    def run_audio_only(self):
        audio = CompositeAudioClip([mp.AudioFileClip("{}/vangelo.mp3".format(self.config.folder))])
        ColorClip((200, 200), (0, 0, 0), duration=audio.duration)\
            .write_videofile("{}/final_video_audio_only.mp4".format(self.config.folder),
                             verbose=False, logger=None, fps=24)

    def add_subs(self, video_clip):
        subtitles = SubtitlesClip("{}/vangelo.srt".format(self.config.folder),
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
    subscribe_prompt_duration = 3

    clips = [VideoFileClip("20230409/video_0.mp4"), VideoFileClip("20230409/video_1.mp4")]

    concatenated = concatenate_videoclips(clips, method="compose").set_start(subscribe_prompt_duration)

    subscribe_image = ImageClip("resources/pope_subscribe.jpeg").set_start(0).set_duration(subscribe_prompt_duration)

    composite = CompositeVideoClip([concatenated, subscribe_image])

    composite \
        .write_videofile("20230409/test.mp4",
                         verbose=True, logger=None)
