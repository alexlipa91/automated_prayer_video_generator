"""Synthesizes speech from the input string of text or ssml.
Make sure to be working in a virtual environment.

Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""
from google.cloud import texttospeech


class TextToSpeech:

    def __init__(self, config, ssml):
        self.config = config
        self.client = texttospeech.TextToSpeechClient()
        self.ssml = ssml

    def translate_file(self):
        synthesis_input = texttospeech.SynthesisInput(ssml=self.ssml)
        voice = texttospeech.VoiceSelectionParams(
            language_code="es-US",
            name="es-US-Neural2-B"
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.75,
            pitch=-5.5
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

