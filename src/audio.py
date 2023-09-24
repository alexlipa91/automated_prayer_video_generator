import os

import requests as requests
import srt as srt
from bs4 import BeautifulSoup
from config import Config


class AudioDownloader:

    def __init__(self, config):
        self.config = config

        self.source_url = "https://www.vaticannews.va/it/vangelo-del-giorno-e-parola-del-giorno/{}/{}/{}.html" \
            .format(config.year, config.month, config.day) if self.config.language == "it" else \
            "https://www.vaticannews.va/es/evangelio-de-hoy/{}/{}/{}.html"\
                .format(config.year, config.month, config.day)

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
        mp3_path = "/output/vangelo.mp3"
        with open(mp3_path, 'wb') as f:
            f.write(doc.content)
        return mp3_path

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

    @staticmethod
    def write_srt(subs):
        srt_file = "/output/vangelo.srt"
        print("Writing subtitles to {}".format(srt_file))
        f = open(srt_file, 'w')
        f.writelines(srt.compose(subs))
        f.close()

    def download_transcript(self):
        file_path = "{}/transcript.txt".format(self.config.output_root)
        print("downloading transcript from {} to {}".format(self.source_url, file_path))
        req = requests.get(self.source_url)
        soup = BeautifulSoup(req.content, "html.parser")

        final_text = ""

        content = soup.findAll('div', attrs={"class": "section__content"})
        for x in content:
            print("new x")
            for p in x.findAll("p"):
                print(p)
                final_text = final_text + p.getText() + " "

        splitted = final_text.split()
        final_text_in_lines = [' '.join(splitted[i: i + 10]) for i in range(0, len(splitted), 10)]

        with open(file_path, "w") as text_file:
            text_file.write('\n'.join(final_text_in_lines))

        return file_path

    def download_transcript_in_multiple_files(self):
        file_path_format = "{}/transcript_<id>.txt".format(self.config.output_root)
        print("downloading transcript in multiple files from {} to {}".format(self.source_url, file_path_format))
        req = requests.get(self.source_url)
        soup = BeautifulSoup(req.content, "html.parser")

        content = soup.findAll('div', attrs={"class": "section__content"})

        # write full file for subs
        full_transcript = ""

        id = 0
        file_paths = []
        for x in content:
            final_text = ""
            for p in x.findAll("p"):
                final_text = final_text + p.getText() + "\n"

            file_path = file_path_format.replace("<id>", str(id))
            with open(file_path, "w") as text_file:
                text_file.write(final_text)

            full_transcript = full_transcript + final_text + "\n"

            id = id + 1
            file_paths.append(file_path)

        full_transcript_path = "{}/full_transcript.txt".format(self.config.output_root)
        with open(full_transcript_path, "w") as text_file:
            text_file.write(full_transcript)

        return file_paths, full_transcript_path


class AudioProcessor:

    def __init__(self, config, mp3_path):
        self.mp3_path = mp3_path
        self.config = config

    def run(self):
        # todo considering warming up model by downloading it in the dockerbuild
        print("Splitting {} using demucs".format(self.mp3_path))
        os.system("demucs {} --out /output --two-stems vocals --mp3 >/dev/null 2>&1".format(self.mp3_path))
        return "/output/htdemucs/vangelo/vocals.mp3"


if __name__ == '__main__':
    ad = AudioDownloader(config=Config(date="2023-09-22", output_root="./tmp", language="es"))
    ad.download_transcript_in_multiple_files()

    #http://usitep.es/apf/reli/citas_biblicas/LIBROSconABREVIATURA.htm