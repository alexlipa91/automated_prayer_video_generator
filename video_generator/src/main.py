import datetime
import os
from pathlib import Path
import time
import shutil
import argparse
# import firebase_admin

from config import Config, get_config_from_args
# import uploader
from audio import DemucsAudioProcessor, VaticanAudioDownloader, VaticanTranscriptDownloader
# from text_to_speech import TextToSpeech
from subtitles import AlignmentGenerator, SubtitlesGenerator
from videos import VideoComposer
# from video_generator.src.video_pexels import VideoDownloader, VideoComposer
# from firebase_admin import firestore


# def build_and_upload_audio_only(config: Config):
#     print(config.__dict__)

#     ad = AudioDownloader(config)
#     mp3_path = ad.download_audio()
#     transcript_path = ad.download_transcript()

#     vc = VideoComposer(config, mp3_path)
#     file_path = vc.run_audio_only()

#     video_id = uploader.upload_audio_only(config, file_path, transcript_path)

# db = firestore.client()
# db.collection('video_uploads').document(config.date).set(
#     {"audio_only_video_id": video_id}, merge=True)


def build_and_upload(config: Config):
    start = time.time()

    VaticanAudioDownloader.with_config(config).run()
    VaticanTranscriptDownloader.with_config(config).run()
    DemucsAudioProcessor.with_config(config).run()
    AlignmentGenerator.with_config(config).run()
    SubtitlesGenerator.with_config(config).run()
    VideoComposer.with_config(config).run()

    # ap = AudioProcessor(config, mp3_path)
    # vocals_mp3_path = ap.run()

    # vd = VideoDownloader(config, vocals_mp3_path)
    # vd.run()

    # vc = VideoComposer(config, vocals_mp3_path)
    # file_path = vc.run()
    # preview_image_path = vc.get_preview_image()

    # video_id = uploader.upload(
    #     config, file_path, preview_image_path, transcript_path)

    # db = firestore.client()
    # db.collection('video_uploads').document(
    #     config.date).set({"video_id": video_id}, merge=True)

    end = time.time()
    print("Done in {} seconds".format(end - start))


# def cleanup():
#     date_to_clean = (datetime.datetime.now() -
#                      datetime.timedelta(days=2)).strftime("%Y-%m-%d")
#     db = firestore.client()

#     video_id = db.collection("video_uploads").document(
#         date_to_clean).get().to_dict()["audio_only_video_id"]
#     uploader.delete(video_id)

#     db.collection("video_uploads").document(date_to_clean).delete()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video generator')
    parser.add_argument('--audio-only', action='store_true',
                        help='generates a video with only the audio')
    parser.add_argument('--date', type=datetime.date,
                        default=datetime.datetime.now().date(), help='date to generate the video for')
    parser.add_argument('--output-dir', type=str, default="output",
                        help='folder relative to the current work dir where to save the output')
    parser.add_argument('--skip-clean-output-dir', action='store_true',
                        help='do not delete the output folder if it exists')
    parser.add_argument('--duration-secs', type=int, default=None,
                        help='cut duration of the video to the specified number of seconds')

    config = get_config_from_args(parser.parse_args())
    print("Running with config: {}".format(config.__dict__))

    # firebase_admin.initialize_app()
    # if os.environ.get("CLEANUP", "0") == "1":
    #     cleanup()
    # elif os.environ.get("AUDIO_ONLY", "0") == "1":
    # if config.audio_only:
    #     build_and_upload_audio_only(config)
    # else:
    build_and_upload(config)
