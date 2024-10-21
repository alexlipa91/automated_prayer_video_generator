import datetime
import logging
import time

from common.runner import Runner
from common.audio import DemucsAudioProcessor
from vangelo.audio import VaticanAudioDownloader, VaticanTranscriptDownloader
from common.subtitles import AlignmentGenerator, SubtitlesGenerator
from common.thumbnail import ThumbnailGenerator
from vangelo.uploader import VaticanYoutubeUploader
from common.videos import VideoComposer

logger = logging.getLogger("root")


class VangeloRunner(Runner):

    def _run_test(self):
        start = time.time()

        VaticanAudioDownloader.with_config(self.config).run()
        DemucsAudioProcessor.with_config(self.config).run()
        VideoComposer.with_config(self.config).run()
        ThumbnailGenerator.with_config(self.config).run()

        end = time.time()
        logger.info("Done in {}".format(
            datetime.timedelta(seconds=end - start)))

    def _run(self):
        start = time.time()

        VaticanAudioDownloader.with_config(self.config).run()
        VaticanTranscriptDownloader.with_config(self.config).run()
        DemucsAudioProcessor.with_config(self.config).run()
        AlignmentGenerator.with_config(self.config).run()
        SubtitlesGenerator.with_config(self.config).run()
        VideoComposer.with_config(self.config).run()
        ThumbnailGenerator.with_config(self.config).run()
        VaticanYoutubeUploader(self.config).run()

        end = time.time()
        logger.info("Done in {}".format(
            datetime.timedelta(seconds=end - start)))
