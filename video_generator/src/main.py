import datetime
from pathlib import Path
import time
import argparse

from config import Config, get_config_from_args
from audio import DemucsAudioProcessor, VaticanAudioDownloader, VaticanTranscriptDownloader
from subtitles import AlignmentGenerator, SubtitlesGenerator
from thumbnail import ThumbnailGenerator
from uploader import YoutubeUploader
from videos import VideoComposer


def run_test_mode(config: Config):
    config.video_duration_secs = 10
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
    YoutubeUploader.with_config(config).run()

    end = time.time()
    print("Done in {}".format(datetime.timedelta(seconds=end - start)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video generator')
    parser.add_argument('--date', type=datetime.date,
                        default=datetime.datetime.now().date(), help='date to generate the video for')
    parser.add_argument('--test-mode', action='store_true',
                        help='run test mode (faster). It skips a bunch of steps')
    config = get_config_from_args(parser.parse_args())

    if config.test_mode:
        run_test_mode(config)
    else:
        run(config)
