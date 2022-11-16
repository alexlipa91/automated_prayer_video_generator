import os

import requests as requests
from mutagen.mp3 import MP3
from bs4 import BeautifulSoup


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
        self.audio_path = "{}/vangelo.mp3".format(self.folder)
        self.audio_duration = 0
        self.transcript_path = "{}/vangelo_transcript.txt".format(self.folder)

    def download_transcript(self):
        print("downloading transcript")
        req = requests.get(self.source_url)
        soup = BeautifulSoup(req.content, "html.parser")

        final_text = ""

        content = soup.findAll('div', attrs={"class": "section__content"})
        for x in content:
            for t in x.findAll("p"):
                final_text = final_text + t.getText()

        splitted = final_text.split()
        final_text_in_lines = [' '.join(splitted[i: i + 10]) for i in range(0, len(splitted), 10)]

        with open(self.transcript_path, "w") as text_file:
            text_file.write('\n'.join(final_text_in_lines))
        print("transcript file saved {}".format(self.transcript_path))

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
        with open(self.audio_path, 'wb') as f:
            f.write(doc.content)

        self.audio_duration = MP3(self.audio_path).info.length
        print("audio file saved {}".format(self.audio_path))

    def generate_srt(self):
        cmd = """
        python -m aeneas.tools.execute_task \
    {}/vangelo.mp3 \
    {}/vangelo_transcript.txt \
    "task_language=ita|os_task_file_format=srt|is_text_type=plain" \
    {}/vangelo.srt
        """.format(self.folder, self.folder, self.folder)
        os.system(cmd)

    def run(self):
        self.download_audio()
        self.download_transcript()


if __name__ == '__main__':
    ad = AudioDownloader(year=2022, month=11, day=10)
    # ad.download_transcript()
    ad.generate_srt()