from abc import ABC, abstractmethod
from pathlib import Path


class PipelineStage(ABC):

    destination_path: Path

    @abstractmethod
    def run(self):
        pass
