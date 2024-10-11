import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
import locale


class Config:

    date: datetime.date = datetime.now().date()
    output_root: Path = Path("output")
    video_duration_secs: Optional[int] = None
    language: str = "it"

    base_video_path: Path = Path("resources/video/base_video_0.mp4")
    background_music_path: Path = Path(
        "resources/background/Drifting at 432 Hz - Unicorn Heads.mp3")
    thumbnail_base_image_path: Path = Path(
        "resources/images/pope_preview_2023.png")

    video_file_name: str = "video.mp4"
    transcript_file_name: str = "transcript.txt"
    alignment_file_name: str = "alignment.txt"
    audio_file_name: str = "audio.mp3"
    thumbnail_file_name: str = "thumbnail.png"
    subs_file_name: Optional[str] = "subs.srt"

    listed: bool = False  # whether the video should be listed on youtube or not

    subs_block_size_seconds: int = 7

    def __init__(self, date: datetime.date = datetime.now().date(), output_root: str = "output", skip_clean_output_dir: bool = False):
        self.date = date
        self.output_root = Path(output_root).joinpath(
            Path(self.date.strftime("%Y-%m-%d")))
        self.skip_clean_output_dir = skip_clean_output_dir

    def init_environment(self):
        # delete the output root if it exists
        if not self.skip_clean_output_dir and self.output_root.exists():
            print(f"Deleting output directory: {self.output_root}")
            shutil.rmtree(self.output_root)
        self.output_root.mkdir(exist_ok=True)
        self.set_locale()

    def set_locale(self):
        locale.setlocale(locale.LC_ALL, str('it_IT'))
        
    @property
    def video_path(self) -> Path:
        return self.output_root.joinpath(self.video_file_name)

    @property
    def audio_path(self) -> Path:
        return self.output_root.joinpath(self.audio_file_name)

    @property
    def transcript_path(self) -> Path:
        return self.output_root.joinpath(self.transcript_file_name)

    @property
    def alignment_path(self) -> Path:
        return self.output_root.joinpath(self.alignment_file_name)

    @property
    def subs_path(self) -> Optional[Path]:
        if self.subs_file_name:
            return self.output_root.joinpath(self.subs_file_name)
        return None

    @property
    def thumbnail_path(self) -> Path:
        return self.output_root.joinpath(self.thumbnail_file_name)


def get_config_from_args(args):
    return Config(date=args.date, output_root=args.output_root, skip_clean_output_dir=args.skip_clean_output_dir)


# def get_config(language="it"):
#     date_param = sys.argv[1] if len(
#         sys.argv) > 1 else os.environ.get("DATE", None)

#     if not date_param:
#         date_param = datetime.now().strftime("%Y-%m-%d")

#     return Config(date_param, language=language)
