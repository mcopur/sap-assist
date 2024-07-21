# nlp/src/api/server.py
import random
from ..utils.entity_extraction import extract_leave_request_info
from ..utils.intent_recognition import classify_intent
from ..utils.validator import validate_leave_request


class Chatbot:
    def __init__(self, model, tokenizer, label_dict, device):
        self.model = model
        self.tokenizer = tokenizer
        self.label_dict = label_dict
        self.device = device
        self.reverse_label_dict = {v: k for k, v in label_dict.items()}
        self.conversation_context = {}
        self.conversation_history = []

    def process_message(self, message):
        self.conversation_history.append(("user", message))

        if 'current_task' in self.conversation_context:
            response = self.continue_task(message)
        else:
            intent_id = classify_intent(
                message, self.model, self.tokenizer, self.label_dict, self.device)
            intent_tag = self.reverse_label_dict[intent_id]
            response = self.handle_intent(intent_tag, message)

        self.conversation_history.append(("bot", response))
        return response

    def handle_intent(self, intent, message):
        if intent == 'greeting':
            return self.generate_response('greeting', {})
        elif intent == 'leave_request_annual':
            self.conversation_context['current_task'] = 'leave_request'
            return "Yıllık izin talebiniz için tarihleri alabilir miyim? Örneğin: 01.08.2024 ve 05.08.2024 arası"
        elif intent == 'leave_request_excuse':
            self.conversation_context['current_task'] = 'leave_request'
            return "Mazeret izni talebiniz için tarih ve saatleri alabilir miyim? Örneğin: 05.08.2024 tarihi 09:30-11:30 arası"
        elif intent == 'purchase_request':
            return "Satın alma talebiniz için hangi ürünü veya hizmeti talep etmek istiyorsunuz?"
        elif intent == 'confirm_annual_leave':
            return "Yıllık izin talebinizi aldım. Onay için yöneticinize ileteceğim. Başka bir isteğiniz var mı?"
        elif intent == 'confirm_excuse_leave':
            return "Mazeret izni talebinizi aldım. Onay için yöneticinize ileteceğim. Başka bir isteğiniz var mı?"
        else:
            return "Üzgünüm, bu tür bir talebi şu anda işleyemiyorum. Lütfen başka bir şekilde ifade etmeyi deneyin."

    def continue_task(self, message):
        task = self.conversation_context['current_task']
        if task == 'leave_request':
            return self.handle_leave_request(message)
        # Diğer görevler için benzer kontroller eklenebilir

    def handle_intent(self, intent, message):
        if intent == 'greeting':
            return self.generate_response('greeting', {})
        elif intent == 'leave_request':
            self.conversation_context['current_task'] = 'leave_request'
            return "İzin talebinizi almak için size birkaç soru soracağım. İlk olarak, hangi tarihler için izin istiyorsunuz?"
        # Diğer niyetler için benzer işlemler

    def handle_leave_request(self, message):
        info = extract_leave_request_info(message)

        is_valid, validation_message = validate_leave_request(
            info['start_date'],
            info['end_date'],
            info['start_time'],
            info['end_time'],
            None  # Duration is not provided in this example
        )

        if not is_valid:
            return f"Üzgünüm, izin talebinizde bir sorun var: {validation_message}"

        self.conversation_context['current_task'] = None  # Task completed
        return self.generate_response('leave_request_confirmation', {
            'start_date': info['start_date'].strftime('%d/%m/%Y'),
            'end_date': info['end_date'].strftime('%d/%m/%Y')
        })

    def generate_response(self, intent, entities):
        responses = {
            'greeting': [
                "Merhaba! Size nasıl yardımcı olabilirim?",
                "Hoş geldiniz! Bugün size nasıl yardımcı olabilirim?",
                "Selam! Nasıl yardımcı olabilirim?"
            ],
            'leave_request_confirmation': [
                "İzin talebinizi aldım. {start_date} ile {end_date} tarihleri arasında izinli görünüyorsunuz. Başka bir şey yapabilir miyim?",
                "Harika! {start_date} - {end_date} tarihleri için izin talebiniz kaydedildi. Başka bir konuda yardımcı olabilir miyim?"
            ]
        }
        return random.choice(responses[intent]).format(**entities)

    def get_feedback(self):
        return "Bu yanıt yardımcı oldu mu? (Evet/Hayır)"

    def process_feedback(self, feedback):
        if feedback.lower() == 'hayır':
            return "Üzgünüm, daha iyi yardımcı olamadım. Lütfen sorunuzu farklı bir şekilde sormayı deneyin veya bir insanla görüşmek için 'insan' yazın."
        return "Teşekkür ederim! Size başka nasıl yardımcı olabilirim?"
