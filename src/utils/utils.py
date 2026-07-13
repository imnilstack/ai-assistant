from __future__ import annotations

import json
from pathlib import Path

from src.config.config import config


class ChatHistoryAppender:
    def __init__(self, history_path: str | Path | None = None) -> None:
        self.history_path = (
            Path(history_path)
            if history_path is not None
            else Path(__file__).resolve().parents[2] / "data" / "chat_history.json"
        )
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

    def load_history(self) -> list[dict[str, str]]:
        if not self.history_path.exists():
            self.history_path.write_text("[]", encoding="utf-8")
            return []

        try:
            data = json.loads(self.history_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []

        if not isinstance(data, list):
            return []

        history: list[dict[str, str]] = []
        for item in data:
            if isinstance(item, dict):
                role = item.get("role")
                content = item.get("content")
                if isinstance(role, str) and isinstance(content, str):
                    history.append({"role": role, "content": content})

        return history

    def append_message(self, role: str, content: str) -> list[dict[str, str]]:
        history = self.load_history()
        history.append({"role": role, "content": content})

        history_config = config.get("history", {})
        chat_history_enabled = history_config.get("chat_history_enabled", False)

        if chat_history_enabled:
            max_history = history_config.get("max_history")

            if isinstance(max_history, int) and max_history > 0:
                max_entries = max_history * 2
                while len(history) > max_entries:
                    del history[:2]

            self._write_history(history)

        return history

    def append_user(self, content: str) -> list[dict[str, str]]:
        return self.append_message("user", content)

    def append_assistant(self, content: str) -> list[dict[str, str]]:
        return self.append_message("assistant", content)

    def _write_history(self, history: list[dict[str, str]]) -> None:
        payload = json.dumps(history, indent=2, ensure_ascii=False)

        tmp_path = self.history_path.with_suffix(f"{self.history_path.suffix}.tmp")
        tmp_path.write_text(payload, encoding="utf-8")
        tmp_path.replace(self.history_path)
