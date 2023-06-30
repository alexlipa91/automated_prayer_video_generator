import os


class Config:

    def __init__(self, date, duration_seconds=None):
        param_tokens = date.split("-")
        self.year = str(param_tokens[0]).zfill(2)
        self.month = str(param_tokens[1]).zfill(2)
        self.day = str(param_tokens[2]).zfill(2)
        self.folder = "{}{}{}".format(self.year, self.month, self.day)

        # if duration seconds is not specified, the audio duration will be used
        self.duration_seconds = duration_seconds
        self.video_parts_max_length_seconds = 15

        try:
            os.mkdir(self.folder)
        except FileExistsError:
            pass


