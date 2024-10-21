from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
import pprint

from common.config import BaseConfig


logger = logging.getLogger("root")


@dataclass
class Runner(ABC):

    config: BaseConfig
    test_mode: bool = False

    def run(self):
        if self.test_mode:
            logger.info("Running Test runner")
            self.config.public_list_youtube = False
            logger.info("Running with config\n{}".format(self.config))
            self._run_test()
        else:
            logger.info("Running Prod runner")
            self.config.public_list_youtube = True
            logger.info("Running with config\n{}".format(self.config))
            self._run()

    @abstractmethod
    def _run(self):
        pass

    @abstractmethod
    def _run_test(self):
        pass
