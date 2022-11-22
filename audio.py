import os

import requests as requests
import srt as srt
from google.cloud import storage
from google.cloud import speech_v1
from bs4 import BeautifulSoup
from pydub import AudioSegment
from pydub.utils import mediainfo


class AudioDownloader:

    def __init__(self, year, month, day):
        self.year = str(year)
        self.month = str(month).zfill(2)
        self.day = str(day).zfill(2)
        self.folder = "{}{}{}".format(self.year, self.month, self.day)
        self.source_url = "https://www.vaticannews.va/it/vangelo-del-giorno-e-parola-del-giorno/{}/{}/{}.html" \
            .format(self.year, self.month, self.day)
        try:
            os.mkdir(self.folder)
        except FileExistsError:
            pass
        self.mp3_path = "{}/vangelo.mp3".format(self.folder)
        self.wav_path = "{}/vangelo.wav".format(self.folder)
        self.wav_gcs_path = "tmp/{}".format(self.wav_path)
        self.transcript_path = "{}/vangelo_transcript.txt".format(self.folder)

    def download_audio(self):
        print("downloading audio")
        url = "https://www.vaticannews.va/it/vangelo-del-giorno-e-parola-del-giorno/{}/{}/{}.html"\
            .format(self.year, self.month, self.day)
        req = requests.get(url)
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

        print("audio file saved {}".format(self.mp3_path))

    @staticmethod
    def video_info(wav_filepath):
        video_data = mediainfo(wav_filepath)
        channels = video_data["channels"]
        bit_rate = video_data["bit_rate"]
        sample_rate = video_data["sample_rate"]

        return channels, bit_rate, sample_rate

    def generate_wav(self):
        AudioSegment.from_mp3(self.mp3_path).export(self.wav_path, format="wav")
        print("wav file saved at {}".format(self.wav_path))

    def upload_wav_to_gcs_blob(self):
        storage_client = storage.Client()
        bucket = storage_client.bucket("nutmeg-9099c.appspot.com")
        blob = bucket.blob(self.wav_gcs_path)

        blob.upload_from_filename(self.wav_path)

        print("File {} uploaded to {}.".format(self.wav_path, self.wav_gcs_path))

    def call_gts_api(self):
        client = speech_v1.SpeechClient()

        channels, bitrate, sample_rate = AudioDownloader.video_info(self.wav_path)

        config = {
            "language_code": "it-IT",
            "sample_rate_hertz": int(sample_rate),
            "encoding": speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
            "audio_channel_count": int(channels),
            "enable_word_time_offsets": True,
            "enable_automatic_punctuation": True
        }
        audio = {"uri": "gs://{}/{}".format("nutmeg-9099c.appspot.com", self.wav_gcs_path)}

        operation = client.long_running_recognize(config=config,
                                                  audio=speech_v1.RecognitionAudio(audio))

        print(u"Waiting for google-text-to-speech operation to complete: {}".format(operation.metadata))
        self.gts_resp = operation.result()
        print("Done")

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

        print("Transcribing finished")
        self.write_srt(subs)

    def write_srt(self, subs):
        srt_file = "{}/vangelo.srt".format(self.folder)
        print("Writing subtitles to {}".format(srt_file))
        f = open(srt_file, 'w')
        f.writelines(srt.compose(subs))
        f.close()

    def run(self):
        self.download_audio()
        self.generate_wav()
        self.upload_wav_to_gcs_blob()
        self.call_gts_api()
        self.generate_subs()


def run(request):
    request_json = request.get_json(silent=True)
    print("args {}, data {}".format(request.args, request_json))

    request_data = request_json["data"]
    AudioDownloader(request_data["year"], request_data["month"], request_data["day"]).run()

    return {}, 200


"""
gcloud functions deploy audio_downloader \
                         --runtime python38 \
                         --entry-point run \
                         --trigger-http \
                         --region europe-central2
"""


if __name__ == '__main__':
    ad = AudioDownloader(year=2022, month=11, day=18)
    ad.run()
