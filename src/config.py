import os
import sys
from datetime import datetime


class Config:

    def __init__(self, date):
        self.date = date
        param_tokens = date.split("-")
        self.year = str(param_tokens[0]).zfill(2)
        self.month = str(param_tokens[1]).zfill(2)
        self.day = str(param_tokens[2]).zfill(2)

        # if duration seconds is not specified, the audio duration will be used
        self.duration_seconds = int(os.environ["DURATION_SECONDS"]) if "DURATION_SECONDS" in os.environ else None
        self.video_parts_max_length_seconds = 15

        self.save_local = int(os.environ.get("SAVE_LOCAL", 0)) == 1
        self.skip_subs = int(os.environ.get("SKIP_SUBS", 0)) == 1
        self.with_background_music = int(os.environ.get("WITH_BACKGROUND_MUSIC", 0)) == 1


def get_config():
    date_param = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("DATE", None)

    if not date_param:
        date_param = datetime.now().strftime("%Y-%m-%d")

    return Config(date_param)

