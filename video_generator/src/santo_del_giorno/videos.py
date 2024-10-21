from dataclasses import dataclass
from typing import Optional
from common.pipeline import WithOutputStage, skip_if_exists
from pathlib import Path
from moviepy.editor import AudioFileClip, CompositeAudioClip, ColorClip
from moviepy.editor import ImageClip, concatenate, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.VideoClip import TextClip


@dataclass
class VideoComposer(WithOutputStage):
    """Composes the final video

    `vocals_mp3` is the path to the vocals mp3 file
    `destination_path` is the path where the final video file will be saved
    """

    base_image: Path
    vocals_mp3: Path
    destination_path: Path
    subs_path: Optional[Path] = None

    # use it for testing to cut the video short
    duration_secs: Optional[int] = None

    def make_subs_clip(self, txt: str):
        width = 800
        height = 200
        color_clip = ColorClip(size=(width+20, height+20),
                               color=(211, 211, 211)).set_opacity(0.5)
        text_clip = TextClip(txt,
                             font='VistaSansOT-RegItalic',
                             method="caption",
                             size=(
                                 width, height),
                             fontsize=48,
                             stroke_width=3,
                             color="white").set_position("center")
        return CompositeVideoClip([color_clip, text_clip])

    def _run(self):
        audio_parts = [AudioFileClip(str(self.vocals_mp3))]
        audio = CompositeAudioClip(audio_parts)
        audio_duration = int(AudioFileClip(str(self.vocals_mp3)).duration)

        clips = [ImageClip(str(self.base_image)).set_duration(
            audio_duration + 1)]
        concat_clips = concatenate(clips, method="compose")

        video_parts = [concat_clips]
        if self.subs_path:
            subs_clip = SubtitlesClip(str(self.subs_path),
                                      lambda txt: self.make_subs_clip(txt=txt)).set_position(("center", "bottom"))
            video_parts.append(subs_clip)

        final_video = CompositeVideoClip(video_parts).set_audio(audio)

        final_video.write_videofile(str(self.destination_path),
                                    remove_temp=True,
                                    audio_codec='aac',
                                    verbose=False,
                                    logger=None,
                                    fps=24)
