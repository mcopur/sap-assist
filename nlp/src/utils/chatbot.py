from nlp.src.utils.logger import ErrorLogger
from nlp.src import utils
import torch
from transformers import AutoTokenizer, BertForSequenceClassification
import pickle
from nlp.src.utils.entity_extraction import extract_entities, extract_date_range
from nlp.src.utils.data_preprocessing import preprocess_text
import logging
from nlp.src.utils.normalizer import normalize_date
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

        self.context = {}
        self.user = None
        self.is_logged_in = False

    def set_user(self, user):
        self.user = user
        self.is_logged_in = True

    def classify_intent(self, text):
        normalized_text = preprocess_text(text)
        inputs = self.tokenizer(
            normalized_text, return_tensors="pt",
            truncation=True, padding=True).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        confidence, predicted_class = torch.max(probabilities, dim=-1)

        intent = self.label_encoder.inverse_transform(
            [predicted_class.item()])[0]
        return intent, confidence.item()

    async def generate_response(self, intent, entities, text):
        try:
            if intent == "greeting":
                return "Merhaba! Size nasıl yardımcı olabilirim?"
            elif intent == "login":
                username = entities.get("PERSON", [None])[0]
                if username:
                    self.set_user(username)
                    return f"Hoş geldiniz, {username}! Nasıl yardımcı olabilirim?"
                else:
                    return "Giriş yapmak için lütfen kullanıcı adınızı belirtin."
            elif intent == "leave_request_annual" or intent == "leave_request_sick":
                if not self.is_logged_in:
                    return "Lütfen önce giriş yapın. Örneğin: 'Kullanıcı adım John Doe' yazabilirsiniz."
                self.context['leave_type'] = 'annual' if intent == "leave_request_annual" else 'sick'
                return f"{'Yıllık' if intent == 'leave_request_annual' else 'Hastalık'} izin talebiniz için hangi tarihler arasında izin almak istiyorsunuz?"
            elif intent == "confirm_annual_leave" or intent == "confirm_excuse_leave":
                if not self.is_logged_in:
                    return "Lütfen önce giriş yapın. Örneğin: 'Kullanıcı adım John Doe' yazabilirsiniz."
                start_date, end_date = extract_date_range(text)
                if not start_date or not end_date:
                    entities = extract_entities(text)
                    dates = entities.get("DATE", [])
                    if len(dates) >= 2:
                        start_date, end_date = dates[:2]

                if start_date and end_date:
                    start_date = normalize_date(start_date)
                    end_date = normalize_date(end_date)
                    leave_type = self.context.get('leave_type', 'annual')
                    response = "Talebiniz işleniyor, lütfen bekleyin..."
                    try:
                        response += f"\n\n{leave_type.capitalize()} izin talebiniz başarıyla alındı ve iletildi. {start_date} ile {end_date} tarihleri arasında izin talebiniz sisteme kaydedildi. Onay durumu hakkında en kısa sürede bilgilendirileceksiniz."
                    except Exception as e:
                        response += f"\n\nÜzgünüm, izin talebiniz işlenirken bir hata oluştu: {str(e)}"
                    return response
                else:
                    return "Üzgünüm, tarih bilgisini anlayamadım. Lütfen tarihleri gün/ay/yıl formatında belirtir misiniz? Örneğin: 01/10/2024 - 05/10/2024"
            elif intent == "purchase_request":
                return "Satın alma talebinizi aldım. Ne satın almak istiyorsunuz ve miktarı nedir?"
            else:
                return "Anladım. Size nasıl yardımcı olabilirim?"
        except Exception as e:
            utils.ErrorLogger.error(f"Error in generate_response: {str(e)}")
            return "Üzgünüm, bir hata oluştu. Lütfen daha sonra tekrar deneyin."

    async def process_message(self, text, context=None):
        try:
            if context:
                self.context.update(context)
            entities = extract_entities(text)
            intent, confidence = self.classify_intent(text)
            response = await self.generate_response(intent, entities, text)
            return {
                "intent": intent,
                "confidence": confidence,
                "entities": entities,
                "response": response
            }
        except Exception as e:
            logger.error(f"Error in process_message: {str(e)}", exc_info=True)
            return {
                "intent": "error",
                "confidence": 1.0,
                "entities": {},
                "response": "Üzgünüm, bir hata oluştu. Lütfen daha sonra tekrar deneyin."
            }
