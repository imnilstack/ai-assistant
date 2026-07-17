# AI Assistant

A simple AI companion/assistant built entirely from scratch in Python.

This project supports customizable personalities, system prompts, model selection, speech-to-text (STT), text-to-speech (TTS), persistent memory, and chat history. It was created as a side project to experiment with building an AI assistant without relying on large frameworks.

## Features

- Customizable personalities
- Customizable system prompts
- Configurable AI model
- Speech-to-text (STT)
- Text-to-speech (TTS)
- Persistent memory
- Saved chat history
- Modular project structure
- Built entirely from scratch in Python

## Requirements

- Python **3.12.x**
- Linux (the only platform currently tested)

## Installation

```bash
git clone <repository-url>
cd ai-assistant

python3.12 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Project Structure

```text
assets/
└── personalities/

data/
├── chat_history.json
├── config.json
└── memory.json

src/
├── ai/
├── chat/
├── config/
├── memory/
├── speech/
├── ui/
└── utils/

tests/
```

## Customization

- Add or edit personalities in `assets/personalities/`.
- Modify application settings in `data/config.json`.
- Conversation history is stored in `data/chat_history.json`.
- Long-term memory is stored in `data/memory.json`.

## Status

This project is a work in progress and is intended primarily as a personal learning and experimentation project.
