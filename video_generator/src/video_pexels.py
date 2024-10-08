import datetime
import glob
import traceback

import requests as requests
from moviepy.audio.fx.volumex import volumex
from pexelsapi.pexels import Pexels
import moviepy.editor as mp
from moviepy.video.tools.subtitles import SubtitlesClip
import random
from mutagen.mp3 import MP3
from moviepy.editor import *
import csv

from firebase_admin import firestore

from thumbnail import Thumbnail
from uploader import find_transcript_auto_synced, download_transcript_srt
from util import get_date_string

WIDTH = 1920
HEIGHT = 1080

BASE_PATH = "output"


class VideoDownloader:

    def __init__(self, config, mp3_path):
        self.config = config

        self.videos = open('resources/videos.csv', 'r').readlines()
        random.shuffle(self.videos)

        if mp3_path:
            self.audio_duration = MP3(mp3_path).info.length

        self.index = 0
        self.duration = 0

    def download_video(self):
        url = self.videos[self.index].strip()
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})

        if r.status_code > 201:
            print(r.text)
            raise Exception("Download request failed with status code {}".format(r.status_code))

        file_name = "{}/video_{}.mp4".format(BASE_PATH, self.index)
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
        resized_video = cut_video.resize((WIDTH, HEIGHT))

        resized_video.write_videofile(file_name, verbose=False, logger=None)

        os.remove(tmp_file_name)

    def run(self):
        target_duration = self.audio_duration if self.config.duration_seconds is None else self.config.duration_seconds

        iterations = 0
        while self.duration < target_duration:
            try:
                self.download_video()
            except Exception:
                print("failed video download {}...skipping it".format(self.index))
            iterations = iterations + 1
            if iterations >= 100:
                raise Exception("Failed video download 100 times, breaking it")
                # traceback.print_exc()


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

    def __init__(self, config, mp3_path):
        self.config = config

        self.background = "resources/scott-buckley-hiraeth.mp3"
        self.mp3_path = mp3_path

    def get_preview_image(self):
        preview_path = "preview.png"
        Thumbnail(self.config.date, preview_path).generate_thumbnail()
        return preview_path

    def run(self):
        parts = []
        print("composing video")
        subscribe_prompt_duration = 3

        clips = [VideoFileClip(f) for f in glob.glob("{}/video_*.mp4".format(BASE_PATH))]
        print("concatenating {} videos".format(len(clips)))
        video = concatenate_videoclips(clips, method="compose").set_start(subscribe_prompt_duration)
        parts.append(video)

        # audio
        audio_parts = [mp.AudioFileClip(self.mp3_path).set_start(subscribe_prompt_duration)]
        if self.config.with_background_music:
            audio_parts.append(mp.AudioFileClip(self.background).fx(volumex, 0.05))
        audio = CompositeAudioClip(audio_parts)
        if self.config.duration_seconds:
            audio = audio.set_duration(self.config.duration_seconds)
        print("audio duration {}".format(audio.duration))

        # subs
        if self.config.skip_subs:
            print("skipping subs")
        else:
            subs_path = self.find_subs()
            if subs_path:
                print("adding subs {}".format(subs_path))
                parts.append(self.get_subs(subs_path, video.size, subscribe_prompt_duration))
            else:
                print("subs not found...skipping")

        # subscribe prompt
        parts.append(ImageClip("resources/pope_subscribe_{}.jpeg".format(self.config.language)).set_start(0)
                     .set_duration(subscribe_prompt_duration)
                     .resize((WIDTH, HEIGHT)))

        final_video = CompositeVideoClip(parts).set_audio(audio)

        file_path = "{}/final_video.mp4".format(BASE_PATH)
        print("writing final video to {}; size is {}".format(file_path, final_video.size))
        final_video \
            .subclip(0, audio.duration + subscribe_prompt_duration) \
            .write_videofile(file_path, verbose=False, logger=None)
        return file_path

    def run_audio_only(self):
        audio = CompositeAudioClip([mp.AudioFileClip(self.mp3_path)])
        file_name = "{}/final_video_audio_only.mp4".format(BASE_PATH)
        ColorClip((200, 200), (0, 0, 0), duration=audio.duration) \
            .set_audio(audio) \
            .write_videofile(file_name, verbose=False, logger=None, fps=24)
        return file_name

    def get_subs(self, subs_path, video_clip_size, start_seconds):
        subtitles = SubtitlesClip(subs_path,
                                  lambda txt: TextClip(txt,
                                                       font='DejaVu-Sans',
                                                       method="caption",
                                                       size=video_clip_size,
                                                       fontsize=48,
                                                       stroke_color="white",
                                                       stroke_width=3,
                                                       # transparent=False,
                                                       color='white')) \
            .set_start(start_seconds) \
            .set_pos('center')
        return subtitles

    def find_subs(self):
        try:
            db = firestore.client()
            audio_only_video_id = db.collection("video_uploads").document(self.config.date).get().to_dict()[
                "audio_only_video_id"]
            print("looking for subs from audio-only video {}".format(audio_only_video_id))

            transcript_id = find_transcript_auto_synced(audio_only_video_id)
            if transcript_id:
                file_name = "{}/vangelo.srt".format(BASE_PATH)
                download_transcript_srt(transcript_id, file_name)
                print("downloading transcript")
                return file_name
            return None
        except Exception:
            print("error when looking for subs")
            traceback.print_exc()
            return None


if __name__ == '__main__':
    # refresh_video_ids()
    d = VideoDownloader(None, None)
    d.download_video()
