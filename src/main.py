import os
import sys
import time

import firebase_admin

import uploader
from audio import AudioDownloader
from config import Config
from video import VideoDownloader, VideoComposer
from datetime import datetime
from firebase_admin import firestore


def build_and_upload_audio_only():
    date_param = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("DATE", None)

    if not date_param:
        date_param = datetime.now().strftime("%Y-%m-%d")

    config = Config(date_param)

    ad = AudioDownloader(config)
    ad.run()

    vc = VideoComposer(config)
    vc.run_audio_only()

    video_id = uploader.upload_audio_only(config)

    db = firestore.client()
    db.collection('video_uploads').document(date_param).set({"audio_only_video_id": video_id})


def build_and_upload():
    start = time.time()

    date_param = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("DATE", None)

    if not date_param:
        date_param = datetime.now().strftime("%Y-%m-%d")

    config = Config(date_param)

    ad = AudioDownloader(config)
    ad.run()

    vd = VideoDownloader(config)
    vd.run()

    vc = VideoComposer(config)
    vc.run()
    vc.generate_preview_pope()

    uploader.upload(config)

    end = time.time()
    print("Done in {} seconds".format(end - start))


if __name__ == '__main__':
    firebase_admin.initialize_app()

    if os.environ.get("AUDIO_ONLY", "0") == "1":
        build_and_upload_audio_only()
    else:
        build_and_upload()
