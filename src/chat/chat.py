from pathlib import Path

from src.ai.gemini import generate_response
from src.config.config import config
from src.speech.tts import TTS

personality = ""

if config["personality"]["enabled"]:
    personality = Path(config["personality"]["path"]).read_text(encoding="utf-8")

if config.get("speech", {}).get("tts_enabled", False):
    tts = TTS(voice=config["speech"].get("voice", "af_bella"))


def start_chat_loop():
    while True:
        msg = input("> ").strip()

        if not msg:
            print(
                "invalid input.\nmust contain at least one letter and cannot be whitespace!"
            )
            continue

        if msg == "exit":
            break

        if personality:
            prompt = f"{personality}\n\nUser:\n{msg}"
        else:
            prompt = msg

        reply = generate_response(prompt)

        print(reply)

        if tts is not None:
            tts.speak(reply)
