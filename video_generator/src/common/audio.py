from pathlib import Path
import subprocess

import requests as requests
import shutil
import srt as srt
from common.config import BaseConfig


from common.pipeline import WithOutputStage, skip_if_exists


class DemucsAudioProcessor(WithOutputStage):
    """
    Uses demucs to split the audio into vocals and accompaniment
    self.destination_path will contain the vocal mp3 file
    """
    @staticmethod
    def with_config(config: BaseConfig):
        return DemucsAudioProcessor(
            original_mp3_path=config.audio_path,
            destination_path=config.audio_path)

    def __init__(self, original_mp3_path: Path, destination_path: Path):
        self.original_mp3_path = original_mp3_path
        self.destination_path = destination_path

    def _run(self):
        parent_path = self.original_mp3_path.parent
        # todo considering warming up model by downloading it in the dockerbuild
        print("Splitting `{}` using demucs and writing to {}".format(
            self.original_mp3_path, self.destination_path))

        p = subprocess.run([
            "demucs",
            self.original_mp3_path,
            "--out",
            str(parent_path),
            "--two-stems",
            "vocals",
            "--mp3",
        ],  stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)
        if p.returncode != 0:
            raise Exception(f"Failed to split audio using demucs")

        # Move the vocals file to the output directory
        vocals_file = parent_path / "htdemucs" / "audio" / "vocals.mp3"
        if vocals_file.exists():
            shutil.move(str(vocals_file), str(self.destination_path))
            print(f"Moved vocals file to {self.destination_path}")
        else:
            raise Exception(
                f"Warning: Expected vocals file not found at {vocals_file}")
