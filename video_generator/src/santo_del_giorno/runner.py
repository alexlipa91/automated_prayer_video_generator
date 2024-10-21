from pathlib import Path

from common.runner import Runner
from common.subtitles import AlignmentGenerator, SubtitlesGenerator
from santo_del_giorno.videos import VideoComposer
import logging

from santo_del_giorno.uploader import YoutubeUploader

logging.basicConfig(level="INFO")


class SantoRunner(Runner):

    def _run_test(self):
        vocals_mp3 = Path(
            "resources/santo_del_giorno/test_audio_sant_orsola.mp3")

        transcript_path = Path("resources/santo_del_giorno/sant_orsola.txt")
        base_path = Path("output/santo_del_giorno")
        alignment = base_path.joinpath("alignment.txt")
        subs = base_path.joinpath("subs.srt")

        video = base_path.joinpath("video.mp4")

        subs_block_size_seconds: int = 5

        AlignmentGenerator(audio_file_path=vocals_mp3,
                           text_file_path=transcript_path,
                           destination_path=alignment).run()
        SubtitlesGenerator(alignment_file_path=alignment,
                           destination_path=subs, subs_block_size_seconds=subs_block_size_seconds).run()

        VideoComposer(base_image=Path("resources/santo_del_giorno/santo_test.webp"),
                      vocals_mp3=vocals_mp3,
                      subs_path=subs,
                      destination_path=video).run()

        YoutubeUploader(date=self.config.date, santo="Sant'Orsola",
                        transcript_path=transcript_path, video=video).run()

    def _run(self):
        self._run_test()
