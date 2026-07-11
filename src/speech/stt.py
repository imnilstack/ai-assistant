import threading

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel


class STT:
    def __init__(
        self,
        model_size="base",
        device="cpu",
        compute_type="int8",
        sample_rate=16000,
        blocksize=512,
        max_listen_duration=None,
    ):
        self.sample_rate = sample_rate
        self.blocksize = blocksize
        self.max_listen_duration = max_listen_duration

        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
        )

    def _wait_for_enter(self, stop_event: threading.Event):
        try:
            input()
        except EOFError:
            pass
        stop_event.set()

    def listen(self):
        print("press enter to start recording...", flush=True)
        try:
            input()
        except EOFError:
            return ""

        stop_event = threading.Event()
        stopper = threading.Thread(
            target=self._wait_for_enter,
            args=(stop_event,),
            daemon=True,
        )
        stopper.start()

        print("recording... press enter again to stop", flush=True)

        audio_chunks = []
        elapsed = 0.0

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            blocksize=self.blocksize,
        ) as stream:
            while not stop_event.is_set():
                chunk, overflowed = stream.read(self.blocksize)

                if overflowed:
                    pass

                chunk = np.asarray(chunk, dtype=np.float32).reshape(-1)
                if chunk.size == 0:
                    continue

                audio_chunks.append(chunk)
                elapsed += chunk.size / self.sample_rate

                if (
                    self.max_listen_duration is not None
                    and elapsed >= self.max_listen_duration
                ):
                    break

        if not audio_chunks:
            return ""

        audio = np.concatenate(audio_chunks).astype(np.float32, copy=False)

        segments, _ = self.model.transcribe(
            audio,
            language="en",
        )

        return "".join(segment.text for segment in segments).strip()
