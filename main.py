import os
import sys

import uploader
from audio import AudioDownloader
from video import VideoDownloader, VideoComposer

if __name__ == '__main__':
    param_tokens = sys.argv[1].split("-")
    year = param_tokens[0]
    month = param_tokens[1]
    day = param_tokens[2]

    ad = AudioDownloader(year=year, month=month, day=day)
    ad.run()

    vd = VideoDownloader(year=year, month=month, day=day)
    vd.run()

    vc = VideoComposer(year=year, month=month, day=day)
    vc.run()

    uploader.upload(year, month, day)