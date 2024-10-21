from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from common.config import BaseConfig


@dataclass
class VangeloConfig(BaseConfig):

    store_firestore_field: str = "video_id"

    base_video_path: Path = Path("resources/video/base_video_0.mp4")
    background_music_path: Path = Path(
        "resources/background/Drifting at 432 Hz - Unicorn Heads.mp3")
    thumbnail_base_image_path: Path = Path(
        "resources/images/pope_preview_2023.png")