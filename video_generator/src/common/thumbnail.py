import datetime
from pathlib import Path
import shutil
from PIL import ImageDraw, Image, ImageFont
from common.util import get_date_string
from common.pipeline import PipelineStage
from common.config import BaseConfig


class ThumbnailGenerator(PipelineStage):

    date: datetime.date
    destination_path: str
    font_path: Path = Path("resources/fonts/WorkSans-VariableFont_wght.ttf")

    @staticmethod
    def with_config(config: BaseConfig):
        return ThumbnailGenerator(date=config.date, base_image_path=config.thumbnail_base_image_path, destination_path=config.thumbnail_path)

    def __init__(self, date: datetime.date, base_image_path: Path = Path("resources/previews/pope_sept_2024.png"), destination_path: Path = Path("output/thumbnail.png")):
        self.date = date
        self.base_image_path = base_image_path
        self.destination_path = destination_path

    def run(self):
        print(f"Generating thumbnail to {self.destination_path}")
        if self.base_image_path == "resources/images/pope_sept_2024.png":
            self.add_text_on_image()
        else:
            print("Simply copying base image to destination")
            self.copy_base_image()

    def copy_base_image(self):
        shutil.copy(self.base_image_path, self.destination_path)

    def add_text_on_image(self):
        img = Image.open(self.base_image_path)

        final_img = ImageDraw.Draw(img)

        date_text = get_date_string(date=self.date, with_year=False)
        font = ImageFont.truetype(str(self.font_path), 37)
        font.set_variation_by_name("Bold")
        final_img.text((250, 510), date_text, fill=(0, 0, 0), font=font)

        img.save(self.destination_path)


if __name__ == "__main__":
    thumbnail = ThumbnailGenerator(datetime.date(
        2024, 9, 1), "/Users/alessandrolipa/Desktop/test_2.png")
    thumbnail.run()
