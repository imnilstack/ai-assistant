from ai.gemini import chat

try:
    while True:
        msg = input("> ")

        if msg == "exit":
            break

        reply = chat(msg)

        print(reply)

except KeyboardInterrupt:
    print("\nbye!")
