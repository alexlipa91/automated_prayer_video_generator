import os
import time

import firebase_admin

import uploader
from audio import AudioDownloader, AudioProcessor
from config import get_config
from text_to_speech import TextToSpeech
from video import VideoDownloader, VideoComposer
from firebase_admin import firestore


def build_and_upload_audio_only():
    config = get_config()
    print(config.__dict__)

    ad = AudioDownloader(config)
    mp3_path = ad.download_audio()
    transcript_path = ad.download_transcript()

    vc = VideoComposer(config, mp3_path)
    file_path = vc.run_audio_only()

    video_id = uploader.upload_audio_only(config, file_path, transcript_path)

    db = firestore.client()
    db.collection('video_uploads').document(config.date).set({"audio_only_video_id": video_id}, merge=True)


def build_and_upload():
    start = time.time()
    config = get_config()
    print(config.__dict__)

    ad = AudioDownloader(config)
    mp3_path = ad.download_audio()
    transcript_path = ad.download_transcript()

    ap = AudioProcessor(config, mp3_path)
    vocals_mp3_path = ap.run()

    vd = VideoDownloader(config, vocals_mp3_path)
    vd.run()

    vc = VideoComposer(config, vocals_mp3_path)
    file_path = vc.run()
    preview_image_path = vc.get_preview_image()

    video_id = uploader.upload(config, file_path, preview_image_path, transcript_path)

    db = firestore.client()
    db.collection('video_uploads').document(config.date).set({"video_id": video_id}, merge=True)

    end = time.time()
    print("Done {} in {} seconds".format(video_id, end - start))


def build_and_upload_es():
    start = time.time()
    config = get_config(language="es")
    config.skip_subs = True
    print(config.__dict__)

    ad = AudioDownloader(config)
    ssml, full_transcript_path = ad.download_transcript_in_ssml()

    # get only the evangelio for now
    t = TextToSpeech(config=config, ssml=ssml)
    mp3_path = t.translate_file()

    vd = VideoDownloader(config, mp3_path)
    vd.run()

    vc = VideoComposer(config, mp3_path)
    file_path = vc.run()
    preview_image_path = vc.get_preview_image()

    video_id = uploader.upload_es(config, file_path, preview_image_path, full_transcript_path)

    db = firestore.client()
    db.collection('video_uploads').document(config.date).set({"video_id_es": video_id}, merge=True)

    end = time.time()
    print("Done {} in {} seconds".format(video_id, end - start))


if __name__ == '__main__':
    firebase_admin.initialize_app()

    if os.environ.get("AUDIO_ONLY", "0") == "1":
        build_and_upload_audio_only()
    elif os.environ.get("LANGUAGE", "IT") == "ES":
        build_and_upload_es()
    else:
        build_and_upload()
