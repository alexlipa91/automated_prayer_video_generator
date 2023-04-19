import os

import requests as requests
import srt as srt
from google.cloud import storage
from bs4 import BeautifulSoup
from pydub import AudioSegment
from pydub.utils import mediainfo
from config import Config


class AudioDownloader:

    def __init__(self, config):
        self.config = config

        self.source_url = "https://www.vaticannews.va/it/vangelo-del-giorno-e-parola-del-giorno/{}/{}/{}.html" \
            .format(config.year, config.month, config.day)
        self.mp3_path = "{}/vangelo.mp3".format(config.folder)
        self.wav_path = "{}/vangelo.wav".format(config.folder)
        self.wav_gcs_path = "tmp/{}".format(self.wav_path)

    def download_audio(self):
        print("downloading audio from {}".format(self.source_url))
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
        with open(self.mp3_path, 'wb') as f:
            f.write(doc.content)

    @staticmethod
    def video_info(wav_filepath):
        video_data = mediainfo(wav_filepath)
        channels = video_data["channels"]
        bit_rate = video_data["bit_rate"]
        sample_rate = video_data["sample_rate"]

        return channels, bit_rate, sample_rate

    def generate_wav(self):
        AudioSegment.from_mp3(self.mp3_path).export(self.wav_path, format="wav")

    def upload_wav_to_gcs_blob(self):
        storage_client = storage.Client()
        bucket = storage_client.bucket("praryers-channel-video-data")
        blob = bucket.blob(self.wav_gcs_path)

        blob.upload_from_filename(self.wav_path)

    @staticmethod
    def _break_sentences(subs, alternative):
        first_word = True
        char_count = 0
        idx = len(subs) + 1
        content = ""

        for w in alternative.words:
            if first_word:
                # first word in sentence, record start time
                start = w.start_time

            char_count += len(w.word)
            content += " " + w.word.strip()

            if ("." in w.word or "!" in w.word or "?" in w.word or
                    char_count > 50 or
                    ("," in w.word and not first_word)):
                # break sentence at: . ! ? or line length exceeded
                # also break if , and not first word
                subs.append(srt.Subtitle(index=idx,
                                         start=start,
                                         end=w.end_time,
                                         content=srt.make_legal_content(content)))
                first_word = True
                idx += 1
                content = ""
                char_count = 0
            else:
                first_word = False
        return subs

    def generate_subs(self):
        subs = []
        for result in self.gts_resp.results:
            # First alternative is the most probable result
            subs = AudioDownloader._break_sentences(subs, result.alternatives[0])

        self.write_srt(subs)

    def write_srt(self, subs):
        srt_file = "{}/vangelo.srt".format(self.config.folder)
        print("Writing subtitles to {}".format(srt_file))
        f = open(srt_file, 'w')
        f.writelines(srt.compose(subs))
        f.close()

    def run(self):
        flag = "{}/audio_downloader_done".format(self.config.folder)
        if os.path.exists(flag):
            print("audio download done...skipping")
            return

        self.download_audio()
        self.download_transcript()

        open(flag, 'x')

    def download_transcript(self):
        print("downloading transcript from {}".format(self.source_url))
        req = requests.get(self.source_url)
        soup = BeautifulSoup(req.content, "html.parser")

        final_text = ""

        content = soup.findAll('div', attrs={"class": "section__content"})
        for x in content:
            last_p = x.findAll("p")[-1]
            final_text = final_text + last_p.getText()

        splitted = final_text.split()
        final_text_in_lines = [' '.join(splitted[i: i + 10]) for i in range(0, len(splitted), 10)]

        with open("{}/transcript.txt".format(self.config.folder), "w") as text_file:
            text_file.write('\n'.join(final_text_in_lines))


if __name__ == '__main__':
    ad = AudioDownloader(config=Config(param="2022-03-03"))
    ad.download_audio()
