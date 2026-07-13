from pathlib import Path

from src.ai.gemini import generate_response
from src.config.config import config
from src.utils.utils import ChatHistoryAppender

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

history_appender = ChatHistoryAppender()
chat_history = history_appender.load_history()


def _get_user_message():
    if stt is not None:
        msg = stt.listen()
        print(f"User: {msg}")
        return msg

    return input("User: ").strip()


def _build_prompt(history: list[dict[str, str]]) -> str:
    prompt_parts = []

    if personality:
        prompt_parts.append(personality.strip())

    for item in history:
        role = item.get("role", "")
        content = item.get("content", "").strip()

        if not content:
            continue

        if role == "user":
            prompt_parts.append(f"User:\n{content}")
        elif role == "assistant":
            prompt_parts.append(f"{name}:\n{content}")

    return "\n\n".join(prompt_parts)


def start_chat_loop():
    global chat_history

    while True:
        msg = _get_user_message().strip()

        if msg.casefold() == "exit":
            break

        if not msg:
            print(
                "invalid input.\nmust contain at least one letter and cannot be whitespace!"
            )
            continue

        chat_history = history_appender.append_user(msg)
        prompt = _build_prompt(chat_history)

        reply = generate_response(prompt)
        if not isinstance(reply, str):
            reply = str(reply)

        print(f"{name}: {reply}\n")

        chat_history = history_appender.append_assistant(reply)

        if tts is not None:
            tts.speak(reply)
