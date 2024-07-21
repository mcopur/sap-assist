# nlp/src/main.py
import torch
from transformers import AutoTokenizer
from src.chatbot.bot import Chatbot
from src.utils.intent_recognition import train_intent_model
from src.utils.data_utils import load_training_data, update_model


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Veri yükleme
    texts, labels, label_dict = load_training_data('data/intent_data.json')

    # Tokenizer yükleme
    tokenizer = AutoTokenizer.from_pretrained(
        "dbmdz/distilbert-base-turkish-cased")

    # Model eğitimi
    model = train_intent_model(
        texts, labels, tokenizer, device, num_labels=len(label_dict))

    # Chatbot oluşturma
    chatbot = Chatbot(model, tokenizer, label_dict, device)

    print("Chatbot: Merhaba! Size nasıl yardımcı olabilirim?")

    while True:
        user_input = input("Siz: ")
        if user_input.lower() == 'çıkış':
            print("Chatbot: Görüşmek üzere!")
            break

        response = chatbot.process_message(user_input)
        print(f"Chatbot: {response}")

        feedback_request = chatbot.get_feedback()
        print(f"Chatbot: {feedback_request}")

        feedback = input("Siz: ")
        feedback_response = chatbot.process_feedback(feedback)
        print(f"Chatbot: {feedback_response}")

        # Eğer kullanıcı geri bildirimi olumsuzsa, yeni veriyi kaydet ve modeli güncelle
        if feedback.lower() == 'hayır':
            new_texts = [user_input]
            new_intent = input("Doğru intent nedir? ")
            if new_intent not in label_dict:
                label_dict[new_intent] = len(label_dict)
            new_labels = [label_dict[new_intent]]
            model, label_dict = update_model(
                new_texts, new_labels, texts, labels, label_dict, tokenizer, device)
            chatbot.model = model
            chatbot.label_dict = label_dict
            chatbot.reverse_label_dict = {v: k for k, v in label_dict.items()}
