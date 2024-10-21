from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
import shutil
import logging
from typing import Optional

logger = logging.getLogger("root")


def skip_if_exists(func):
    def inner(self):
        if self.destination_path.exists:
            logger.info(format("Skipping {}: destination {} exists".format(
                type(self).__name__, self.destination_path)))
        else:
            func(self)
    return inner


class Stage(ABC):

    @abstractmethod
    def run(self):
        pass


class WithOutputStage(Stage):

    destination_path: Path

    def run(self):
        if self.destination_path.exists:
            logger.info(format("Skipping {}: destination {} exists".format(
                type(self).__name__, self.destination_path)))
        else:
            logger.warn("Running {}".format(type(self).__name__,  "with destination path {}".format(
                self.destination_path) if self.destination_path else ""))
            self._run()
