import glob
import os

import requests as requests
from pexelsapi.pexels import Pexels
import moviepy.editor as mp
from moviepy.video.VideoClip import TextClip
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
import random

from audio import AudioDownloader


class VideoDownloader:

    def __init__(self, year, month, day):
        self.year = str(year)
        self.month = str(month).zfill(2)
        self.day = str(day).zfill(2)
        self.folder = "{}{}{}".format(self.year, self.month, self.day)

        self.videos = open('videos.csv', 'r').readlines()
        random.shuffle(self.videos)

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

    # def create_final_video(self):
    #     existing_clips = [VideoFileClip(f) for f in glob.glob("{}/*.mp4".format(self.folder))]
    #
    #     clips_to_concatenate = []
    #     total_duration = 0
    #
    #     while total_duration < self.audio_duration:
    #         for c in existing_clips:
    #             clips_to_concatenate.append(c)
    #             total_duration = total_duration + c.duration
    #             if total_duration > self.audio_duration:
    #                 pass
    #
    #     concatenated = concatenate_videoclips(clips_to_concatenate, method="compose")
    #
    #     audio = mp.AudioFileClip(self.audio_path)
    #
    #     with_audio = concatenated.set_audio(audio)
    #     final_clip = with_audio.subclip(0, audio.duration)
    #
    #     final_clip.write_videofile("{}/final_video.mp4".format(self.folder))

    def run(self, audio_duration):
        while self.duration < audio_duration:
            print("missing duration: {}".format(audio_duration - self.duration))
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

    def __init__(self, folder, total_duration):
        self.folder = folder
        self.total_duration = total_duration

    def run(self):
        clips = [VideoFileClip(f) for f in glob.glob("{}/*.mp4".format(self.folder))]

        concatenated = concatenate_videoclips(clips, method="compose")

        audio = mp.AudioFileClip("{}/vangelo.mp3".format(self.folder))

        with_audio = concatenated.set_audio(audio)

        subtitles = SubtitlesClip("{}/vangelo.srt".format(self.folder),
                                  lambda txt: TextClip(txt, font='Georgia-Regular', fontsize=24, color='white'))
        with_subtitles = CompositeVideoClip([with_audio, subtitles])

        final_clip = with_subtitles.subclip(0, audio.duration)

        final_clip.write_videofile("{}/final_video.mp4".format(self.folder))


if __name__ == '__main__':
    # todo youtube uploader
    # todo verify random sample of videos

    # ad = AudioDownloader(year=2022, month=11, day=10)
    # ad.run()

    # vd = VideoDownloader(year=2022, month=11, day=10)
    # vd.run(ad.audio_duration)

    v = VideoComposer(folder="20221110", total_duration=221)
    v.run()

