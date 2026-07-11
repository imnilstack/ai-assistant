import sounddevice as sd
from faster_whisper import WhisperModel


class STT:
    def __init__(
        self,
        model_size="base",
        device="cpu",
        compute_type="int8",
        sample_rate=16000,
    ):
        self.sample_rate = sample_rate

        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
        )

    def listen(self, seconds=5):
        print("Listening...")

        audio = sd.rec(
            int(seconds * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
        )

        sd.wait()

        segments, _ = self.model.transcribe(
            audio.flatten(),
            language="en",
        )

        return "".join(segment.text for segment in segments).strip()
