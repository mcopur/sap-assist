
from intent_recognition import classify_intent
from entity_extraction import extract_leave_request_info
from textblob import TextBlob
import random
import json
import os


class Chatbot:
    def __init__(self, model, tokenizer, label_dict, device):
        self.model = model
        self.tokenizer = tokenizer
        self.label_dict = label_dict
        self.device = device
        self.context = {}
        self.conversation_state = "INITIAL"
        self.conversation_history = []
        self.load_memory()

    def process_message(self, message):
        self.conversation_history.append(("user", message))

        intent, confidence = classify_intent(
            message, self.model, self.tokenizer, self.label_dict, self.device)
        entities = extract_leave_request_info(message)
        sentiment = self.analyze_sentiment(message)

        if sentiment < -0.5:
            response = self.handle_negative_sentiment()
        elif self.conversation_state == "WAITING_FOR_LEAVE_DATES":
            response = self.handle_leave_dates(message, entities)
        elif self.conversation_state == "WAITING_FOR_PURCHASE_DETAILS":
            response = self.handle_purchase_details(message, entities)
        else:
            response = self.handle_intent(intent, message, entities)

        self.conversation_history.append(("bot", response))
        self.save_memory()
        return response

    def handle_intent(self, intent, message, entities):
        if intent == "greeting":
            return self.handle_greeting()
        elif intent == "leave_request_annual":
            self.conversation_state = "WAITING_FOR_LEAVE_DATES"
            self.context["leave_type"] = "annual"
            return self.ask_for_leave_dates()
        elif intent == "leave_request_excuse":
            self.conversation_state = "WAITING_FOR_LEAVE_DATES"
            self.context["leave_type"] = "excuse"
            return self.ask_for_leave_dates()
        elif intent == "purchase_request":
            self.conversation_state = "WAITING_FOR_PURCHASE_DETAILS"
            return self.ask_for_purchase_details()
        elif intent == "confirm_annual_leave" or intent == "confirm_excuse_leave":
            return self.handle_leave_confirmation(message, entities)
        else:
            return self.handle_unknown_intent()

    def handle_greeting(self):
        greetings = [
            "Merhaba! Size nasıl yardımcı olabilirim?",
            "Hoş geldiniz! Bugün size nasıl yardımcı olabilirim?",
            "Selam! Nasıl yardımcı olabilirim?",
        ]
        return random.choice(greetings)

    def ask_for_leave_dates(self):
        if self.context["leave_type"] == "annual":
            prompts = [
                "Yıllık izin talebiniz için tarihleri alabilir miyim? Örneğin: 01.08.2024 ve 05.08.2024 arası",
                "Hangi tarihler arasında yıllık izin kullanmak istiyorsunuz? Lütfen başlangıç ve bitiş tarihlerini belirtin.",
            ]
        else:
            prompts = [
                "Mazeret izni talebiniz için tarih ve saatleri alabilir miyim? Örneğin: 05.08.2024 tarihi 09:30-11:30 arası",
                "Mazeret izniniz için hangi gün ve saatler arasında izin almak istiyorsunuz?",
            ]
        return random.choice(prompts)

    def handle_leave_dates(self, message, entities):
        if not entities["is_valid"]:
            return f"Üzgünüm, izin talebinizde bir sorun var: {entities['validation_message']}"

        self.context.update(entities)
        self.conversation_state = "INITIAL"
        return self.confirm_leave_request()

    def confirm_leave_request(self):
        leave_type = "Yıllık İzin" if self.context["leave_type"] == "annual" else "Mazeret İzni"
        start_date = self.context["start_date"]
        end_date = self.context.get("end_date")
        start_time = self.context.get("start_time")
        end_time = self.context.get("end_time")
        duration = self.context.get("duration")
        person = self.context.get("person", "")
        organization = self.context.get("organization", "")

        confirmation = f"İzin talebinizi aldım. İzin türü: {leave_type}, "
        if person:
            confirmation += f"Talep eden: {person}, "
        if organization:
            confirmation += f"Organizasyon: {organization}, "
        confirmation += f"Başlangıç: {start_date}"
        if start_time:
            confirmation += f" {start_time}"
        if end_date:
            confirmation += f", Bitiş: {end_date}"
            if end_time:
                confirmation += f" {end_time}"
        elif duration:
            confirmation += f", Süre: {duration} dakika"

        return f"{confirmation}. Onay için yöneticinize ileteceğim. Başka bir isteğiniz var mı?"

    def ask_for_purchase_details(self):
        return "Satın alma talebiniz için hangi ürünü veya hizmeti talep etmek istiyorsunuz? Lütfen detayları belirtin."

    def handle_purchase_details(self, message, entities):
        self.context["purchase_details"] = message
        self.conversation_state = "INITIAL"
        person = entities.get("person", "")
        organization = entities.get("organization", "")

        confirmation = f"Satın alma talebinizi aldım: {message}. "
        if person:
            confirmation += f"Talep eden: {person}. "
        if organization:
            confirmation += f"Organizasyon: {organization}. "
        confirmation += "Talebinizi ilgili departmana ileteceğim. Başka bir isteğiniz var mı?"

        return confirmation

    def handle_unknown_intent(self):
        responses = [
            "Üzgünüm, ne demek istediğinizi tam olarak anlayamadım. Lütfen daha açık bir şekilde ifade edebilir misiniz?",
            "Sanırım sizi yanlış anladım. Lütfen talebinizi başka bir şekilde ifade etmeyi dener misiniz?",
            "Ne istediğinizi anlayamadım. Lütfen daha fazla bilgi verebilir misiniz?",
        ]
        return random.choice(responses)

    def analyze_sentiment(self, text):
        blob = TextBlob(text)
        return blob.sentiment.polarity

    def handle_negative_sentiment(self):
        responses = [
            "Üzgün görünüyorsunuz. Size nasıl yardımcı olabilirim?",
            "Sizi rahatsız eden bir şey var gibi görünüyor. Bunu konuşmak ister misiniz?",
            "Endişeli görünüyorsunuz. Size nasıl destek olabilirim?",
        ]
        return random.choice(responses)

    def load_memory(self):
        if os.path.exists("chatbot_memory.json"):
            with open("chatbot_memory.json", "r") as f:
                self.context = json.load(f)

    def save_memory(self):
        with open("chatbot_memory.json", "w") as f:
            json.dump(self.context, f)

    def reset_context(self):
        self.context = {}
        self.conversation_state = "INITIAL"
        self.conversation_history = []

    def handle_leave_confirmation(self, message, entities):
        # Bu metod, izin talebini onaylamak için kullanılabilir
        # Şu anda sadece basit bir onay mesajı döndürüyoruz
        return "İzin talebinizi onayladım. İyi tatiller!"
