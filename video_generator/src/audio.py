import datetime
import os
from pathlib import Path
import subprocess
from typing import Optional

import bs4
import requests as requests
import shutil
import srt as srt
from bs4 import BeautifulSoup
from config import Config

from pydub import AudioSegment

from pipeline import PipelineStage


class VaticanAudioDownloader(PipelineStage):

    source_url: str
    destination_path: Path

    duration_secs: Optional[int]

    @staticmethod
    def with_config(config: Config):
        return VaticanAudioDownloader(
            date=config.date,
            language=config.language,
            destination_path=config.audio_path,
            duration_secs=config.video_duration_secs)

    def __init__(self, date: datetime.date, destination_path: Path, language: str = "it", duration_secs: Optional[int] = None):
        self.source_url = get_vatican_source_url(date, language)
        self.destination_path = destination_path
        self.duration_secs = duration_secs

    def maybe_cut_to_secs(self):
        if not self.duration_secs:
            return

        audio = AudioSegment.from_mp3(self.destination_path)

        first_x_seconds = audio[:self.duration_secs*1000]
        first_x_seconds.export(self.destination_path, format="mp3")

    def run(self) -> Path:
        print("downloading audio from {} into {}".format(
            self.source_url, self.destination_path))
        req = requests.get(self.source_url)
        soup = BeautifulSoup(req.content, "html.parser")
        src = None
        for m in soup.findAll('audio'):
            src = m.get("src", None)
            if src:
                break
        if not src:
            raise Exception("Not able to parse source to get audio url")

        doc = requests.get(src)
        with open(self.destination_path, 'wb') as f:
            f.write(doc.content)

        self.maybe_cut_to_secs()


class VaticanTranscriptDownloader(PipelineStage):

    @staticmethod
    def with_config(config: Config):
        return VaticanTranscriptDownloader(
            date=config.date,
            language=config.language,
            destination_path=config.transcript_path)

    def __init__(self, date: datetime.date, destination_path: Path, language: str = "it"):
        self.source_url = get_vatican_source_url(date, language)
        self.destination_path = destination_path

    def process_div(self, div: list[bs4.element.Tag], text_tokens: list[str]) -> list[str]:
         for p in div:
            for c in p.contents:
                if not c.name == "br":
                    text_tokens.append(c.getText().strip())
                    
    def run(self):
        print("downloading transcript from {} to {}".format(
            self.source_url, self.destination_path))
        req = requests.get(self.source_url)
        soup = BeautifulSoup(req.content, "html.parser")

        content = soup.findAll('div', attrs={"class": "section__content"})
        divs = [div.findAll("p") for div in content]
        final_texts = []

        # prima lettura
        prima_lettura = divs[0]
        starting_idx = 2 if len(prima_lettura[0].findAll("b")) > 0 else 0
        prima_lettura = prima_lettura[starting_idx:]
        self.process_div(prima_lettura, final_texts)
        
        final_texts.extend(["", ""])
        
        seconda_lettura = divs[1]
        self.process_div(seconda_lettura, final_texts)
        
        final_texts.extend(["", ""])
        
        omelia = divs[2]
        self.process_div(omelia, final_texts)

        with open(self.destination_path, "w") as text_file:
            text_file.write('\n'.join(final_texts))


class DemucsAudioProcessor(PipelineStage):
    """
    Uses demucs to split the audio into vocals and accompaniment
    self.destination_path will contain the vocal mp3 file
    """
    @staticmethod
    def with_config(config: Config):
        return DemucsAudioProcessor(
            original_mp3_path=config.audio_path,
            destination_path=config.audio_path)

    def __init__(self, original_mp3_path: Path, destination_path: Path):
        self.original_mp3_path = original_mp3_path
        self.destination_path = destination_path

    def run(self):
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


def get_vatican_source_url(date: datetime.date, language: str = "it"):
    url_date_part = "{}/{}/{}".format(str(date.year).zfill(
        2), str(date.month).zfill(2), str(date.day).zfill(2))
    if language == "it":
        return "https://www.vaticannews.va/it/vangelo-del-giorno-e-parola-del-giorno/{}.html".format(
            url_date_part)
    if language == "es":
        return "https://www.vaticannews.va/es/evangelio-de-hoy/{}".format(
            url_date_part)
    raise Exception("Language not supported")


if __name__ == "__main__":
    VaticanTranscriptDownloader.with_config(Config()).run()
