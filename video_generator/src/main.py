import datetime
from pathlib import Path
import time
import argparse

from config import Config, get_config_from_args
from audio import DemucsAudioProcessor, VaticanAudioDownloader, VaticanTranscriptDownloader
from subtitles import AlignmentGenerator, SubtitlesGenerator
from thumbnail import ThumbnailGenerator
from videos import VideoComposer


def run(config: Config):
    start = time.time()

    VaticanAudioDownloader.with_config(config).run()
    VaticanTranscriptDownloader.with_config(config).run()
    DemucsAudioProcessor.with_config(config).run()
    AlignmentGenerator.with_config(config).run()
    SubtitlesGenerator.with_config(config).run()
    VideoComposer.with_config(config).run()
    ThumbnailGenerator.with_config(config).run()

    # todo upload

    end = time.time()
    print("Done in {} seconds".format(end - start))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video generator')
    parser.add_argument('--audio-only', action='store_true',
                        help='generates a video with only the audio')
    parser.add_argument('--date', type=datetime.date,
                        default=datetime.datetime.now().date(), help='date to generate the video for')
    parser.add_argument('--output-dir', type=str, default="output",
                        help='folder relative to the current work dir where to save the output')
    parser.add_argument('--skip-clean-output-dir', action='store_true',
                        help='do not delete the output folder if it exists')
    parser.add_argument('--duration-secs', type=int, default=None,
                        help='cut duration of the video to the specified number of seconds')

    config = get_config_from_args(parser.parse_args())
    print("Running with config: {}".format(config.__dict__))

    run(config)
