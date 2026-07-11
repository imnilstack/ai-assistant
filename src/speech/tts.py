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

    def _iter_chunks(self, text: str):
        for _, _, audio in self.pipeline(text, voice=self.voice):
            yield np.asarray(audio, dtype=np.float32)

    def generate(self, text: str) -> np.ndarray:
        chunks = list(self._iter_chunks(text))
        if not chunks:
            return np.empty((0,), dtype=np.float32)
        return np.concatenate(chunks)

    def speak(self, text: str):
        with sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
        ) as stream:
            for chunk in self._iter_chunks(text):
                if chunk.ndim == 1:
                    chunk = chunk[:, None]  # mono -> (frames, 1)
                stream.write(chunk)

    def save(self, text: str, filename: str | Path):
        with sf.SoundFile(
            filename,
            mode="w",
            samplerate=self.sample_rate,
            channels=1,
            subtype="PCM_16",
        ) as f:
            for chunk in self._iter_chunks(text):
                f.write(chunk)
