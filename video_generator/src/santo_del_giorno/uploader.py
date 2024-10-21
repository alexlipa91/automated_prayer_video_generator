import datetime
from pathlib import Path
from common.uploader import YoutubeUploader


class YoutubeUploader(YoutubeUploader):
    def __init__(self, santo: str, transcript_path: Path, date: datetime.date, video: Path, listed: bool = False):
        title = santo
        description = """
Santo del giorno: {}.
        
#santodelgiorno
#shorts
# vaticannews 
        
A casa vostra, ogni giorno

Prodotti Consigliati: 
- Bibbia ufficiale CEI: https://amzn.to/4eEIfAu

----------------

{}
        """.format(santo, open(transcript_path).read())
        tags = ["short", "santo", "santodelgiorno", "preghiere", "chiesa",
                "gesù", "bibbia", "vaticano", "papa", "francesco", "omelia"]
        category = "22"
        super().__init__(
            date=date,
            title=title,
            description=description,
            tags=tags,
            category=category,
            video_file=video,
            privacy_status="public" if listed else "unlisted",
            store_firestore_field="santo_del_giorno_video_id",
        )
