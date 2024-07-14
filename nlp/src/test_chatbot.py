from src.chatbot.bot import Chatbot
import sys
import os

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))


def test_chatbot():
    bot = Chatbot()

    test_messages = [
        "Merhaba",
        "İzin almak istiyorum",
        "Yeni bir bilgisayar sipariş etmek istiyorum",
        "Bu nasıl çalışıyor?"
    ]

    for message in test_messages:
        response = bot.process_message(message)
        print(f"User: {message}")
        print(f"Bot: {response}")
        print()


if __name__ == "__main__":
    test_chatbot()
