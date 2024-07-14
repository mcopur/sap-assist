import re
from intent_recognition import classify_intent
import sys
import os

# Proje kök dizinini Python yoluna ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Chatbot:
    def __init__(self, model, tokenizer, label_dict, device):
        self.model = model
        self.tokenizer = tokenizer
        self.label_dict = label_dict
        self.device = device
        self.context = {}

    def process_message(self, message):
        intent, confidence = classify_intent(
            message, self.model, self.tokenizer, self.label_dict, self.device)

        if intent == "greeting":
            return "Merhaba! Size nasıl yardımcı olabilirim?"
        elif intent == "leave_request_annual":
            return "Yıllık izin talebiniz için tarihleri alabilir miyim? Örneğin: 01.08.2024 ve 05.08.2024 arası"
        elif intent == "leave_request_excuse":
            return "Mazeret izni talebiniz için tarih ve saatleri alabilir miyim? Örneğin: 05.08.2024 tarihi 09:30-11:30 arası"
        elif intent == "purchase_request":
            return "Satın alma talebiniz için hangi ürünü veya hizmeti talep etmek istiyorsunuz?"
        elif intent == "confirm_annual_leave":
            dates = self.extract_dates(message)
            if dates:
                return f"Yıllık izin talebinizi aldım. İzin türü: Yıllık İzin, Başlangıç: {dates[0]}, Bitiş: {dates[1]}. Onay için yöneticinize ileteceğim. Başka bir isteğiniz var mı?"
            else:
                return "Üzgünüm, tarih bilgilerini anlayamadım. Lütfen 'GG.AA.YYYY ve GG.AA.YYYY' formatında iki tarih belirtin."
        elif intent == "confirm_excuse_leave":
            date, time_range = self.extract_date_and_time(message)
            if date and time_range:
                return f"Mazeret izni talebinizi aldım. İzin türü: Mazeret İzni, Tarih: {date}, Saat: {time_range}. Onay için yöneticinize ileteceğim. Başka bir isteğiniz var mı?"
            else:
                return "Üzgünüm, tarih ve saat bilgilerini anlayamadım. Lütfen 'GG.AA.YYYY tarihi SS:DD-SS:DD' formatında belirtin."
        else:
            return "Üzgünüm, ne demek istediğinizi anlayamadım. Lütfen daha açık bir şekilde ifade eder misiniz?"

    def extract_dates(self, message):
        date_pattern = r'\d{2}\.\d{2}\.\d{4}'
        dates = re.findall(date_pattern, message)
        return dates if len(dates) == 2 else None

    def extract_date_and_time(self, message):
        date_pattern = r'\d{2}\.\d{2}\.\d{4}'
        time_pattern = r'\d{2}:\d{2}-\d{2}:\d{2}'
        dates = re.findall(date_pattern, message)
        times = re.findall(time_pattern, message)
        return (dates[0], times[0]) if dates and times else (None, None)

    def reset_context(self):
        self.context = {}
