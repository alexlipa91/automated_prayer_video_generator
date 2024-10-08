from typing import Any, Optional
from pipeline import PipelineStage
from config import Config
from pathlib import Path
from moviepy.editor import AudioFileClip, CompositeAudioClip, CompositeVideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.tools.subtitles import SubtitlesClip


class VideoComposer(PipelineStage):
    """Composes the final video

    `vocals_mp3` is the path to the vocals mp3 file
    `destination_path` is the path where the final video file will be saved
    """

    source_video_path: Path = Path("resources/video/base_video_0.mp4")

    # use it for testing to cut the video short
    duration_secs: Optional[int]

    @staticmethod
    def with_config(config: Config):
        return VideoComposer(vocals_mp3=config.audio_path, destination_path=config.video_path, subs_path=config.subs_path)

    def __init__(self, vocals_mp3: Path, destination_path: Path, subs_path: Optional[Path] = None, duration_secs: Optional[int] = None):
        self.vocals_mp3 = vocals_mp3
        self.destination_path = destination_path
        self.subs_path = subs_path
        self.duration_secs = duration_secs

    def run(self):
        # audio
        start_audio_at = 1
        audio_parts = [AudioFileClip(
            str(self.vocals_mp3)).set_start(start_audio_at)]
        audio = CompositeAudioClip(audio_parts)

        # video
        video_parts = [VideoFileClip(str(self.source_video_path))]

        if self.subs_path:
            video_parts.append(SubtitlesClip(str(self.subs_path),
                                             lambda txt: TextClip(txt,
                                                                  font='DejaVu-Sans',
                                                                  method="caption",
                                                                  size=(
                                                                      1000, 200),
                                                                  fontsize=48,
                                                                  stroke_color="white",
                                                                  stroke_width=3,
                                                                  # transparent=False,
                                                                  color='white')) \
                               .set_position(("center", 850))
                               .set_start(start_audio_at))

        video = CompositeVideoClip(video_parts)

        # write
        final_video = CompositeVideoClip(video_parts).set_audio(
            audio)

        if self.duration_secs:
            final_video = final_video.set_duration(self.duration_secs)

        print("writing final video to {}".format(self.destination_path))
        final_video.write_videofile(
            str(self.destination_path), verbose=False, logger=None)


if __name__ == "__main__":
    video_composer = VideoComposer(
        vocals_mp3=Path("output/audio.mp3"),
        destination_path=Path("output/video.mp4"),
        subs_path=Path("output/subs.srt"),
        duration_secs=10
    )
    video_composer.run()
