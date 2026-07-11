from ai.gemini import chat

try:
    while True:
        msg = input("> ").strip()

        if not msg:
            print(
                "invalid input.\nmust contain at least one letter and cannot be whitespace!",
            )
            continue

        if msg == "exit":
            break

        reply = chat(msg)

        print(reply)

except KeyboardInterrupt:
    print("\nbye!")
