import datetime
from common.uploader import YoutubeUploader
from vangelo.config import Config


class VaticanYoutubeUploader(YoutubeUploader):
    def __init__(self, c: Config):
        title = "Vangelo del Giorno - {}".format(
            c.date.strftime("%A %d %B %Y").title())
        description = """
Vangelo e letture del giorno, con commento del Santo Padre.
        
Offerto da: https://www.vaticannews.va/it
#vangelo
#vangelodelgiorno
#papafrancesco
#vaticannews 
        
A casa vostra, ogni giorno

Prodotti Consigliati: 
- Bibbia ufficiale CEI: https://amzn.to/4eEIfAu

----------------


{}        
        """.format(open(c.transcript_path).read())
        tags = ["vangelo", "preghiere", "chiesa",
                "gesù", "bibbia", "vaticano", "papa", "francesco", "omelia"]
        category = "22"
        playlist_id = "PLYFkvAawma-UGoEyPMwnsmzJtYut-wie7"
        super().__init__(
            date=datetime.datetime.now().date(),
            title=title,
            description=description,
            tags=tags,
            category=category,
            video_file=c.video_path,
            thumbnail_file=c.thumbnail_path,
            privacy_status="public" if c.listed else "unlisted",
            playlist_id=playlist_id,
            store_firestore=c.store_firestore,
        )
