from chat.chat import start_chat_loop

try:
    start_chat_loop()

except KeyboardInterrupt:
    print("\ncya!")
