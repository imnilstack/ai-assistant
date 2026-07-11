from pathlib import Path

from src.ai.gemini import generate_response
from src.config.config import config

personality = ""

if config["personality"]["enabled"]:
    personality = Path(config["personality"]["path"]).read_text(encoding="utf-8")


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
