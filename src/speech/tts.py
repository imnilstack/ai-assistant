from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf
from kokoro import KPipeline


class TTS:
    def __init__(
        self,
        voice: str = "af_bella",
        lang: str = "a",
        sample_rate: int = 24000,
    ):
        self.voice = voice
        self.sample_rate = sample_rate
        self.pipeline = KPipeline(lang_code=lang, repo_id="hexgrad/Kokoro-82M")

    def generate(self, text: str) -> np.ndarray:
        chunks = []

        for _, _, audio in self.pipeline(
            text,
            voice=self.voice,
        ):
            chunks.append(audio)

        return np.concatenate(chunks)

    def speak(self, text: str):
        audio = self.generate(text)
        sd.play(audio, self.sample_rate)
        sd.wait()

    def save(self, text: str, filename: str | Path):
        audio = self.generate(text)
        sf.write(filename, audio, self.sample_rate)
