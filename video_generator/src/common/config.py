from dataclasses import dataclass
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
import locale
import firebase_admin
import os


@dataclass
class BaseConfig:

    date: datetime.date = datetime.now().date()
    
    skip_clean_output_dir: bool = False
    output_root: Path = Path("output")
    
    video_duration_secs: Optional[int] = None
    language: str = "it"

    video_file_name: str = "video.mp4"
    transcript_file_name: str = "transcript.txt"
    audio_file_name: str = "audio.mp3"
    thumbnail_file_name: str = "thumbnail.png"
    subs_file_name: Optional[str] = "subs.srt"
    subs_block_size_seconds: int = 3

    listed: bool = True  # whether the video should be listed on youtube or not
    store_firestore: bool = True

    def init_environment(self):
        # delete the output root if it exists
        if not self.skip_clean_output_dir and self.output_root.exists():
            print(f"Deleting output directory: {self.output_root}")
            shutil.rmtree(self.output_root)
        os.makedirs(self.output_root, exist_ok=True)
        self.set_locale()

    def set_locale(self):
        locale.setlocale(locale.LC_ALL, str('it_IT.UTF-8'))

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
