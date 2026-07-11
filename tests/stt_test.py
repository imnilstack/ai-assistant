from src.speech.stt import STT

stt = STT()

text = stt.listen()

print(text)
