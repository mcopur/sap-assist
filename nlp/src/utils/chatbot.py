import torch
from transformers import AutoTokenizer, BertForSequenceClassification
import pickle
from nlp.src.utils.entity_extraction import extract_entities
from nlp.src.utils.data_preprocessing import preprocess_text
import logging

logger = logging.getLogger(__name__)


class Chatbot:
    def __init__(self, model_path, label_encoder_path):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = BertForSequenceClassification.from_pretrained(
            model_path).to(self.device)

        with open(label_encoder_path, 'rb') as f:
            self.label_encoder = pickle.load(f)

        logger.info(f"Successfully loaded model and label encoder")

    def classify_intent(self, text):
        normalized_text = preprocess_text(text)
        inputs = self.tokenizer(
            normalized_text, return_tensors="pt", truncation=True, padding=True).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        confidence, predicted_class = torch.max(probabilities, dim=-1)

        intent = self.label_encoder.inverse_transform(
            [predicted_class.item()])[0]
        return intent, confidence.item()

    def generate_response(self, intent, entities):
        responses = {
            "greeting": "Merhaba! Size nasıl yardımcı olabilirim?",
            "leave_request_annual": "Yıllık izin talebinizi aldım. Hangi tarihler için izin almak istiyorsunuz?",
            "leave_request_sick": "Geçmiş olsun. Hastalık izni talebinizi aldım. Hangi tarihler için izin almak istiyorsunuz?",
            "purchase_request": "Satın alma talebinizi aldım. Ne satın almak istiyorsunuz ve miktarı nedir?",
            "confirm_annual_leave": self.format_leave_confirmation(entities),
            "default": "Anladım. Size nasıl yardımcı olabilirim?"
        }
        return responses.get(intent, responses["default"])

    def format_leave_confirmation(self, entities):
        dates = entities.get('DATE', [])
        if len(dates) >= 2:
            return f"Anladım. {dates[0]} ile {dates[1]} tarihleri arasında yıllık izin talebinizi aldım. Onaylamak için yöneticinize iletiyorum. Başka bir isteğiniz var mı?"
        elif len(dates) == 1:
            return f"Anladım. {dates[0]} tarihinde yıllık izin talebinizi aldım. Tam olarak hangi tarihler arasında izin almak istediğinizi belirtebilir misiniz?"
        else:
            return "Yıllık izin talebinizi aldım, ancak tarih bilgisi eksik görünüyor. Hangi tarihler için izin almak istiyorsunuz?"

    def process_message(self, text):
        entities = extract_entities(text)
        intent, confidence = self.classify_intent(text)
        response = self.generate_response(intent, entities)

        return {
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "response": response
        }
