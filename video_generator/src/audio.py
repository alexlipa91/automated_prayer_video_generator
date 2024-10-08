import datetime
import os
from pathlib import Path
import subprocess

import requests as requests
import shutil
import srt as srt
from bs4 import BeautifulSoup
from config import Config


from pipeline import PipelineStage


class VaticanAudioDownloader(PipelineStage):

    source_url: str
    destination_path: Path

    @staticmethod
    def with_config(config: Config):
        return VaticanAudioDownloader(
            date=config.date,
            language=config.language,
            destination_path=config.audio_path)

    def __init__(self, date: datetime.date, destination_path: Path, language: str = "it"):
        self.source_url = get_vatican_source_url(date, language)
        self.destination_path = destination_path

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

    # @staticmethod
    # def _break_sentences(subs, alternative):
    #     first_word = True
    #     char_count = 0
    #     idx = len(subs) + 1
    #     content = ""

    #     for w in alternative.words:
    #         if first_word:
    #             # first word in sentence, record start time
    #             start = w.start_time

    #         char_count += len(w.word)
    #         content += " " + w.word.strip()

    #         if ("." in w.word or "!" in w.word or "?" in w.word or
    #                 char_count > 50 or
    #                 ("," in w.word and not first_word)):
    #             # break sentence at: . ! ? or line length exceeded
    #             # also break if , and not first word
    #             subs.append(srt.Subtitle(index=idx,
    #                                      start=start,
    #                                      end=w.end_time,
    #                                      content=srt.make_legal_content(content)))
    #             first_word = True
    #             idx += 1
    #             content = ""
    #             char_count = 0
    #         else:
    #             first_word = False
    #     return subs

    # def generate_subs(self):
    #     subs = []
    #     for result in self.gts_resp.results:
    #         # First alternative is the most probable result
    #         subs = AudioDownloader._break_sentences(
    #             subs, result.alternatives[0])

    #     self.write_srt(subs)

    # @staticmethod
    # def write_srt(subs):
    #     srt_file = "/output/vangelo.srt"
    #     print("Writing subtitles to {}".format(srt_file))
    #     f = open(srt_file, 'w')
    #     f.writelines(srt.compose(subs))
    #     f.close()


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

    def run(self):
        print("downloading transcript from {} to {}".format(
            self.source_url, self.destination_path))
        req = requests.get(self.source_url)
        soup = BeautifulSoup(req.content, "html.parser")

        final_text = ""

        content = soup.findAll('div', attrs={"class": "section__content"})
        for index_div, div in enumerate(content):
            for index_p, paragraph in enumerate(div.findAll("p")):
                if index_div == 0 and index_p == 0 and len(paragraph.findAll("b")) > 0:
                    # skip "santo del giorno"
                    continue
                final_text = final_text + paragraph.getText() + " "

        splitted = final_text.split()
        final_text_in_lines = [' '.join(splitted[i: i + 10])
                               for i in range(0, len(splitted), 10)]

        with open(self.destination_path, "w") as text_file:
            text_file.write('\n'.join(final_text_in_lines))


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
    VaticanTranscriptDownloader(date=datetime.date(
        2024, 10, 4), destination_path=Path("output/transcript.txt")).run()
    # DemucsAudioProcessor(original_mp3_path=Path("output/audio.mp3"), destination_path=Path("output/audio_vocals.mp3")).run()
