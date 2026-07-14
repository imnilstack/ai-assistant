from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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


class MemoryManager:
    def __init__(self, memory_path: str | Path | None = None) -> None:
        self.memory_path = (
            Path(memory_path)
            if memory_path is not None
            else Path(__file__).resolve().parents[2] / "data" / "memory.json"
        )
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)

    def load_memories(self) -> list[dict[str, Any]]:
        if not self.memory_path.exists():
            self.memory_path.write_text("[]", encoding="utf-8")
            return []

        try:
            data = json.loads(self.memory_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []

        if not isinstance(data, list):
            return []

        memories: list[dict[str, Any]] = []
        for item in data:
            normalized = self._normalize_memory_item(item)
            if normalized is not None:
                memories.append(normalized)

        return memories

    def apply_memory_update(self, update: dict[str, Any]) -> list[dict[str, Any]]:
        if not isinstance(update, dict):
            return self.load_memories()

        memories = self.load_memories()

        for remove_item in update.get("remove", []):
            content = self._get_content(remove_item)
            if not content:
                continue
            memories = [m for m in memories if m.get("content") != content]

        for replace_item in update.get("replace", []):
            if not isinstance(replace_item, dict):
                continue

            old_content = replace_item.get("old_content")
            new_item = replace_item.get("new")

            if not isinstance(old_content, str):
                continue

            normalized_new = self._normalize_memory_item(new_item)
            if normalized_new is None:
                continue

            for index, memory in enumerate(memories):
                if memory.get("content") == old_content:
                    memories[index] = normalized_new
                    break

        existing_contents = {memory.get("content") for memory in memories}

        for add_item in update.get("add", []):
            normalized_add = self._normalize_memory_item(add_item)
            if normalized_add is None:
                continue

            content = normalized_add["content"]
            if content in existing_contents:
                continue

            memories.append(normalized_add)
            existing_contents.add(content)

        memories = self._deduplicate_memories(memories)
        self._write_memories(memories)
        return memories

    def _normalize_memory_item(self, item: Any) -> dict[str, Any] | None:
        if not isinstance(item, dict):
            return None

        content = item.get("content")
        description = item.get("description", "")
        memory_weight = item.get("memory_weight", 1)

        if not isinstance(content, str):
            return None

        content = content.strip()
        if not content:
            return None

        if not isinstance(description, str):
            description = str(description)

        try:
            memory_weight = int(memory_weight)
        except (TypeError, ValueError):
            memory_weight = 1

        memory_weight = max(1, min(10, memory_weight))

        return {
            "content": content,
            "description": description.strip(),
            "memory_weight": memory_weight,
        }

    def _get_content(self, item: Any) -> str | None:
        if not isinstance(item, dict):
            return None

        content = item.get("content")
        if isinstance(content, str):
            content = content.strip()
            return content or None

        return None

    def _deduplicate_memories(
        self, memories: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        seen: set[str] = set()
        deduped: list[dict[str, Any]] = []

        for memory in memories:
            content = memory.get("content")
            if not isinstance(content, str):
                continue

            key = content.casefold()
            if key in seen:
                continue

            seen.add(key)
            deduped.append(memory)

        return deduped

    def _write_memories(self, memories: list[dict[str, Any]]) -> None:
        payload = json.dumps(memories, indent=2, ensure_ascii=False)

        tmp_path = self.memory_path.with_suffix(f"{self.memory_path.suffix}.tmp")
        tmp_path.write_text(payload, encoding="utf-8")
        tmp_path.replace(self.memory_path)
