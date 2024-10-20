from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from common.config import BaseConfig


@dataclass
class Config(BaseConfig):

    base_video_path: Path = Path("resources/video/base_video_0.mp4")
    background_music_path: Path = Path(
        "resources/background/Drifting at 432 Hz - Unicorn Heads.mp3")
    thumbnail_base_image_path: Path = Path(
        "resources/images/pope_preview_2023.png")
    
    alignment_file_name: str = "alignment.txt"

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
