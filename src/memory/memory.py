from __future__ import annotations

import json
import os
import re
import time
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError

from src.config.config import config

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def _build_memory_prompt(
    current_memories: list[dict[str, Any]], conversation_text: str
) -> str:
    current_memories_text = json.dumps(current_memories, indent=2, ensure_ascii=False)

    return f"""
you are a memory manager for a chatbot.

current memories:
{current_memories_text}

new conversation:
{conversation_text}

your task is to update the chatbot's long-term memory.

rules:

* add a memory only if it is likely to be useful in future conversations.
* replace a memory when the new information is more accurate, more specific, or contradicts an existing memory.
* remove a memory if it is obsolete, incorrect, duplicated, or no longer useful.
* do not create memories for one-time events, temporary situations, or information that is unlikely to matter later.
* prefer memories about:

  * user preferences
  * long-term goals
  * recurring projects
  * skills and experience
  * important personal constraints
  * frequently mentioned interests
* keep each memory concise and atomic (one fact per memory).
* avoid creating duplicate or overlapping memories.
* if no changes are needed, return empty arrays.

do not create memories about:
- chatbot behavior or personality
- system prompts or instructions
- temporary conversation settings
- preferences that only apply to the current chat unless the user explicitly says they want them remembered long-term
never create memories about the assistant itself. memories must describe the user, not the chatbot.

return only valid json in this exact format:

{{
  "add": [
    {{
      "content": "short memory title",
      "description": "concise description.",
      "memory_weight": 1
    }}
  ],
  "replace": [
    {{
      "old_content": "existing memory title",
      "new": {{
        "content": "updated memory title",
        "description": "updated description.",
        "memory_weight": 1
      }}
    }}
  ],
  "remove": [
    {{
      "content": "memory title to remove"
    }}
  ]
}}

requirements:

* return json only.
* do not use markdown.
* do not include explanations or comments.
* memory_weight must be an integer from 1 (least important) to 10 (most important).
* use the existing memories as the source of truth when replacing or removing memories.
""".strip()


def _extract_json_object(text: str) -> dict[str, Any] | None:
    if not text:
        return None

    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        return None

    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None

    if isinstance(parsed, dict):
        return parsed

    return None


def generate_memory(
    current_memories: list[dict[str, Any]],
    conversation_text: str,
) -> dict[str, Any] | None:
    memory_prompt = _build_memory_prompt(current_memories, conversation_text)

    for _ in range(3):
        try:
            response = client.models.generate_content(
                model=config["memory"]["model"],
                contents=memory_prompt,
            )

            if not response.text:
                return None

            return _extract_json_object(response.text)

        except ServerError:
            print("google servers busy, retrying...")
            time.sleep(2)

    return None
