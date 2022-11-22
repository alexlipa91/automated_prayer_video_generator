import os

import uploader
from audio import AudioDownloader
from video import VideoDownloader, VideoComposer

if __name__ == '__main__':
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "prayers-channel-369405-3b2a01d84758.json"
    year = 2022
    month = 11
    day = 20

    ad = AudioDownloader(year=year, month=month, day=day)
    ad.run()

    vd = VideoDownloader(year=year, month=month, day=day)
    vd.run()

    vc = VideoComposer(year=year, month=month, day=day)
    vc.run()

    uploader.upload(year, month, day)