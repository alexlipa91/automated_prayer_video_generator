from typing import Any, Optional
from pipeline import PipelineStage
from config import Config
from pathlib import Path
from moviepy.editor import AudioFileClip, CompositeAudioClip, CompositeVideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.audio.fx.volumex import volumex


class VideoComposer(PipelineStage):
    """Composes the final video

    `vocals_mp3` is the path to the vocals mp3 file
    `destination_path` is the path where the final video file will be saved
    """

    source_video_path: Path = Path("resources/video/base_video_0.mp4")
    background_volume_multiplier: float = 0.05

    # use it for testing to cut the video short
    duration_secs: Optional[int]

    @staticmethod
    def with_config(config: Config):
        return VideoComposer(vocals_mp3=config.audio_path, background_mp3_path=config.background_music_path, destination_path=config.video_path, subs_path=config.subs_path, duration_secs=config.video_duration_secs)

    def __init__(self, vocals_mp3: Path, background_mp3_path: Path, destination_path: Path, subs_path: Optional[Path] = None, duration_secs: Optional[int] = None):
        self.vocals_mp3 = vocals_mp3
        self.destination_path = destination_path
        self.subs_path = subs_path
        self.duration_secs = duration_secs
        self.background_mp3_path = background_mp3_path

    def get_video_duration_secs(self) -> Optional[int]:
        if self.duration_secs:
            return self.duration_secs
        # if both vocal and background are provided, use the vocal duration + a buffer
        if self.background_mp3_path:
            return int(AudioFileClip(str(self.vocals_mp3)).duration) + 10
        return None

    def run(self):
        # audio
        start_audio_at = 1

        audio_parts = [AudioFileClip(
            str(self.vocals_mp3)).set_start(start_audio_at)]
        if self.background_mp3_path:
            audio_parts.append(AudioFileClip(
                str(self.background_mp3_path)).fx(volumex, self.background_volume_multiplier))

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
                               .set_position(("center", 825))
                               .set_start(start_audio_at))

        video = CompositeVideoClip(video_parts)

        # write
        final_video = CompositeVideoClip(video_parts).set_audio(
            audio)

        video_duration_secs = self.get_video_duration_secs()
        if video_duration_secs:
            print("setting video duration to {}".format(video_duration_secs))
            final_video = final_video.set_duration(video_duration_secs)

        print("writing final video to {}".format(self.destination_path))
        final_video.write_videofile(
            str(self.destination_path), verbose=False, logger=None)


if __name__ == "__main__":
    video_composer = VideoComposer(
        vocals_mp3=Path("output/2024-10-09/audio.mp3"),
        background_mp3_path=Path(
            "resources/background/Drifting at 432 Hz - Unicorn Heads.mp3"),
        destination_path=Path("output/2024-10-09/video.mp4"),
        # subs_path=Path("output/subs.srt"),
        duration_secs=20
    )
    video_composer.run()
