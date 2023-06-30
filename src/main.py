import os
import sys
import time

import uploader
from audio import AudioDownloader
from config import Config
from video import VideoDownloader, VideoComposer
from datetime import datetime


def build_and_upload_audio_only():
    date_param = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("DATE", None)

    if not date_param:
        date_param = datetime.now().strftime("%Y-%m-%d")

    config = Config(date_param)

    ad = AudioDownloader(config)
    ad.run()

    vc = VideoComposer(config)
    vc.run_audio_only()

    uploader.upload_audio_only(config)


def build_and_upload():
    start = time.time()

    date_param = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("DATE", None)

    if not date_param:
        date_param = datetime.now().strftime("%Y-%m-%d")

    config = Config(date_param)

    ad = AudioDownloader(config)
    ad.run()

    vd = VideoDownloader(config)
    vd.run()

    vc = VideoComposer(config)
    vc.run()
    vc.generate_preview_pope()

    uploader.upload(config)

    end = time.time()
    print("Done in {} seconds".format(end - start))


if __name__ == '__main__':
    if os.environ.get("AUDIO_ONLY", "0") == "1":
        build_and_upload_audio_only()
    else:
        build_and_upload()
