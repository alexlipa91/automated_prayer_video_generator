import datetime
import time
import argparse

from vangelo.config import Config
from common.audio import DemucsAudioProcessor
from vangelo.audio import VaticanAudioDownloader, VaticanTranscriptDownloader
from common.subtitles import AlignmentGenerator, SubtitlesGenerator
from common.thumbnail import ThumbnailGenerator
from vangelo.uploader import VaticanYoutubeUploader
from common.videos import VideoComposer


def run_test_mode(config: Config):
    config.subs_file_name = None
    config.skip_clean_output_dir = True

    print("Running with config: {}".format(config.__dict__))
    config.init_environment()

    start = time.time()

    VaticanAudioDownloader.with_config(config).run()
    DemucsAudioProcessor.with_config(config).run()
    VideoComposer.with_config(config).run()
    ThumbnailGenerator.with_config(config).run()

    end = time.time()
    print("Done in {}".format(datetime.timedelta(seconds=end - start)))


def run(config: Config):
    print("Running with config: {}".format(config.__dict__))
    config.init_environment()

    start = time.time()

    VaticanAudioDownloader.with_config(config).run()
    VaticanTranscriptDownloader.with_config(config).run()
    DemucsAudioProcessor.with_config(config).run()
    AlignmentGenerator.with_config(config).run()
    SubtitlesGenerator.with_config(config).run()
    VideoComposer.with_config(config).run()
    ThumbnailGenerator.with_config(config).run()
    VaticanYoutubeUploader(config).run()

    end = time.time()
    print("Done in {}".format(datetime.timedelta(seconds=end - start)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video generator')
    parser.add_argument('--date', type=datetime.date,
                        default=datetime.datetime.now().date(), help='date to generate the video for')
    parser.add_argument('--test-mode', action='store_true',
                        help='run test mode (faster). It skips a bunch of steps')

    cli_args = parser.parse_args()
    config = Config(date=cli_args.date)

    if cli_args.test_mode:
        run_test_mode(config)
    else:
        run(config)
