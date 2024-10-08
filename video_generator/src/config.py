import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class Config:

    language: str = "it"
    date: datetime.date
    audio_only: bool
    video_duration_secs: Optional[int]

    base_video_path: Path = Path("resources/video/base_video_0.mp4")

    video_path: Path
    transcript_path: Path
    audio_path: Path
    subs_block_size_seconds: int = 7

    def __init__(self, date: datetime.date, output_root: str, audio_only: bool, video_duration_secs: Optional[int] = None, skip_clean_output_dir: bool = False):
        self.date = date
        self.audio_only = audio_only
        self.video_duration_secs = video_duration_secs

        output_root_path = Path().absolute().joinpath(output_root)
        # delete the output root if it exists
        if not skip_clean_output_dir and output_root_path.exists():
            print(f"Deleting output directory: {output_root_path}")
            shutil.rmtree(output_root_path)
        output_root_path.mkdir(exist_ok=True)

        self.video_path = output_root_path.joinpath("video.mp4")
        self.audio_path = output_root_path.joinpath("audio.mp3")
        self.transcript_path = output_root_path.joinpath("transcript.txt")
        self.alignment_path = output_root_path.joinpath("alignment.txt")
        self.subs_path = output_root_path.joinpath("subs.srt")

        # if duration seconds is not specified, the audio duration will be used
        # self.duration_seconds = int(
        #     os.environ["DURATION_SECONDS"]) if "DURATION_SECONDS" in os.environ else None
        # self.video_parts_max_length_seconds = 15

        # self.save_local = int(os.environ.get("SAVE_LOCAL", 0)) == 1
        # self.skip_subs = int(os.environ.get("SKIP_SUBS", 0)) == 1
        # self.with_background_music = int(
        #     os.environ.get("WITH_BACKGROUND_MUSIC", 0)) == 1


def get_config_from_args(args):
    return Config(date=args.date, output_root=args.output_dir, audio_only=args.audio_only,
                  skip_clean_output_dir=args.skip_clean_output_dir, video_duration_secs=args.duration_secs)


# def get_config(language="it"):
#     date_param = sys.argv[1] if len(
#         sys.argv) > 1 else os.environ.get("DATE", None)

#     if not date_param:
#         date_param = datetime.now().strftime("%Y-%m-%d")

#     return Config(date_param, language=language)
