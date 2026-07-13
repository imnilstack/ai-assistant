from pathlib import Path

from src.ai.gemini import generate_response
from src.config.config import config

personality = ""
tts = None
stt = None
name = config["personality"]["name"]

if config.get("personality", {}).get("enabled", False):
    personality = Path(config["personality"]["path"]).read_text(encoding="utf-8")

speech_config = config.get("speech", {})

if speech_config.get("tts_enabled", False):
    from src.speech.tts import TTS

    tts = TTS(voice=speech_config.get("voice", "af_bella"))

if speech_config.get("stt_enabled", False):
    from src.speech.stt import STT

    stt = STT(
        model_size=speech_config.get("stt_model", "base"),
        device=speech_config.get("stt_device", "cpu"),
        compute_type=speech_config.get("stt_compute_type", "int8"),
    )


def _get_user_message():
    if stt is not None:
        msg = stt.listen()
        print(f"User: {msg}")
        return msg

    return input("User: ").strip()


def start_chat_loop():
    while True:
        msg = _get_user_message()

        if msg.casefold() == "exit":
            break

        if not msg:
            print(
                "invalid input.\nmust contain at least one letter and cannot be whitespace!"
            )
            continue

        if personality:
            prompt = f"{personality}\n\nUser:\n{msg}"
        else:
            prompt = msg

        reply = generate_response(prompt)

        print(f"{name}:", reply, "\n")

        if tts is not None:
            tts.speak(reply)
