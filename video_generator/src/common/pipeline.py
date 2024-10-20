from abc import ABC, abstractmethod
from pathlib import Path


class PipelineStage:

    destination_path: Path

    def run(self):
        pass
