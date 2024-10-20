import datetime
from pathlib import Path
from typing import Optional

import bs4
import requests

from common.pipeline import PipelineStage
from vangelo.config import Config
from pydub import AudioSegment
from vangelo.config import Config


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
        soup = bs4.BeautifulSoup(req.content, "html.parser")
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
        soup = bs4.BeautifulSoup(req.content, "html.parser")

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
