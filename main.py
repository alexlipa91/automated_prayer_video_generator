import os
import sys
import time

import uploader
from audio import AudioDownloader
from video import VideoDownloader, VideoComposer


class Config:

    def __init__(self, param):
        param_tokens = param.split("-")
        self.year = str(param_tokens[0]).zfill(2)
        self.month = str(param_tokens[1]).zfill(2)
        self.day = str(param_tokens[2]).zfill(2)
        self.folder = "{}{}{}".format(self.year, self.month, self.day)
        try:
            os.mkdir(self.folder)
        except FileExistsError:
            pass


if __name__ == '__main__':
    start = time.time()

    config = Config(sys.argv[1])

    ad = AudioDownloader(config)
    ad.run()

    vd = VideoDownloader(config)
    vd.run()

    vc = VideoComposer(config)
    vc.run()

    uploader.upload(config)

    end = time.time()

    open("done", "x")
    print("Done in {} seconds".format(end - start))
