import os
import sys
import time

import uploader
from audio import AudioDownloader
from config import Config
from video import VideoDownloader, VideoComposer
from datetime import datetime


if __name__ == '__main__':
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
    vc.generate_preview()

    uploader.upload(config)

    end = time.time()

    open("done", "x")
    print("Done in {} seconds".format(end - start))

