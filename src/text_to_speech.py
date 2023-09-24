"""Synthesizes speech from the input string of text or ssml.
Make sure to be working in a virtual environment.

Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""
from google.cloud import texttospeech

from config import Config


class TextToSpeech:

    def __init__(self, config, files):
        self.config = config
        self.client = texttospeech.TextToSpeechClient()
        self.files = files

    def translate_file(self):
        synthesis_input = texttospeech.SynthesisInput(ssml=self.create_ssml())
        voice = texttospeech.VoiceSelectionParams(
            language_code="es-US",
            name="es-US-Neural2-B"
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.9,
            pitch=-1.5
        )
        response = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        mp3_path = "{}/evangelio.mp3".format(self.config.output_root)
        # The response's audio_content is binary.
        with open(mp3_path, "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)
            print('Audio content written to file {}'.format(mp3_path))
        return mp3_path

    def create_ssml(self):
        file_ssml = []
        for file in self.files:
            lines = []
            with open(file, "r") as f:
                lines = f.readlines()
            file_ssml.append("""{}<break time="2s"/>{}""".format(lines[0], lines[2]))

        ssml = """<speak>{}<break time="5s"/>{}</speak>""".format(file_ssml[0], file_ssml[1])

        return ssml


if __name__ == '__main__':
    t = TextToSpeech(config=Config(date="2023-09-23", output_root="./tmp"),
                     files=["./tmp/transcript_0.txt", "./tmp/transcript_1.txt"])
    t.translate_file()
