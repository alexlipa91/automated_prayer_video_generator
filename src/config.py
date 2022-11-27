import os


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
