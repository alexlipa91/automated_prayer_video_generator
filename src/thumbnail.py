import datetime
from PIL import ImageDraw, Image, ImageFont
from util import get_date_string

class Thumbnail:

    date: datetime.date
    destination_path: str
    
    def __init__(self, date: datetime.date, destination_path: str):
        self.date = date
        self.destination_path = destination_path

    def generate_thumbnail(self) -> None:

        img = Image.open('resources/previews/pope_sept_2024.png')

        final_img = ImageDraw.Draw(img)
        
        date_text = get_date_string(date=self.date, with_year=False)
        font = ImageFont.truetype("resources/fonts/WorkSans-VariableFont_wght.ttf", 37)
        font.set_variation_by_name("Bold")
        final_img.text((250, 510), date_text, fill=(0, 0, 0), font=font)

        img.save(self.destination_path)        


if __name__ == "__main__":
    thumbnail = Thumbnail(datetime.date(2024, 9, 1), "/Users/alessandrolipa/Desktop/test_2.png")
    thumbnail.generate_thumbnail()