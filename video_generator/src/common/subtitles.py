from datetime import timedelta
from pathlib import Path
import subprocess

from common.pipeline import WithOutputStage, skip_if_exists
from common.config import BaseConfig

from datetime import timedelta
from srt import Subtitle, compose


class AlignmentGenerator(WithOutputStage):
    """Generates a txt alignment file given a audio file and a text transcript file"""

    @staticmethod
    def with_config(config: BaseConfig):
        return AlignmentGenerator(
            audio_file_path=config.audio_path,
            text_file_path=config.transcript_path,
            destination_path=config.alignment_path)

    def __init__(self, audio_file_path: Path, text_file_path: Path, destination_path: Path):
        self.audio_file_path = audio_file_path
        self.text_file_path = text_file_path
        self.destination_path = destination_path

    def _run(self):
        p = subprocess.Popen([
            "ctc-forced-aligner",
            "--audio_path",
            self.audio_file_path,
            "--text_path",
            self.text_file_path,
            "--language",
            "it",
            "--romanize"
        ])
        p.wait()
        if p.returncode != 0:
            raise Exception(
                f"Failed to generate alignment file")
        else:
            expected_path = self.audio_file_path.parent / \
                (self.audio_file_path.stem + ".txt")
            if not expected_path.exists():
                raise Exception(
                    f"Expected alignment file {expected_path} to exist")
            expected_path.rename(self.destination_path)
            print(
                f"Alignment file {self.destination_path} generated successfully")


class SubtitlesGenerator(WithOutputStage):
    """Generates a srt subtitle file given a txt alignment file"""

    @staticmethod
    def with_config(config: BaseConfig):
        return SubtitlesGenerator(
            alignment_file_path=config.alignment_path,
            destination_path=config.subs_path,
            subs_block_size_seconds=config.subs_block_size_seconds)

    def __init__(self, alignment_file_path: Path, destination_path: Path, subs_block_size_seconds: int):
        self.alignment_file_path = alignment_file_path
        self.destination_path = destination_path
        self.subs_block_size = timedelta(seconds=subs_block_size_seconds)

    def get_timedelta(self, timestamp: str) -> timedelta:
        return timedelta(seconds=int(timestamp.split(".")[0]), milliseconds=int(timestamp.split(".")[1]))

    def merge_in_block(self, subs: list[Subtitle]) -> list[Subtitle]:
        new_subs = []

        current_index = 0
        current_start = subs[0].start
        current_end = subs[0].end
        current_content = [subs[0].content]

        for sub in subs[1:]:
            if sub.end - current_start > self.subs_block_size:
                new_subs.append(Subtitle(index=current_index, start=current_start,
                                end=current_end, content=" ".join(current_content)))

                current_index = current_index + 1
                current_start = sub.start
                current_end = sub.end
                current_content = [sub.content]
            else:
                current_content.append(sub.content)
                current_end = sub.end

        new_subs.append(Subtitle(index=current_index, start=current_start,
                        end=current_end, content=" ".join(current_content)))

        return new_subs

    @skip_if_exists
    def run(self):
        # read alignment file
        subs = []
        with open(self.alignment_file_path, "r") as f:
            alignment_segments = f.readlines()

            # if start = end, then the content is carried over to the next segment
            carried_over_content = []

            for index, alignment_segment in enumerate(alignment_segments):
                timestamps, content = alignment_segment.strip().split(": ")
                start = self.get_timedelta(timestamps.split("-")[0])
                end = self.get_timedelta(timestamps.split("-")[1])

                if start == end:
                    carried_over_content.append(content)
                else:
                    if len(carried_over_content) > 0:
                        to_write = " ".join(
                            carried_over_content) + " " + content
                        carried_over_content = []
                    else:
                        to_write = content
                    subs.append(Subtitle(index=index, start=start,
                                end=end, content=to_write))

            if len(carried_over_content) > 0:
                subs.append(Subtitle(index=index+1, start=end+timedelta(milliseconds=1),
                            end=end+timedelta(milliseconds=2), content=" ".join(carried_over_content)))

        composed_subs = compose(self.merge_in_block(subs))
        # write to file
        with open(self.destination_path, "w") as f:
            f.write(composed_subs)


if __name__ == "__main__":
    AlignmentGenerator.with_config(Config()).run()
