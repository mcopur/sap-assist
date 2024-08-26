# nlp/src/utils/chatbot.py
from nlp.src.utils.data_preprocessing import preprocess_text
from nlp.src.utils.entity_extraction import extract_entities
from nlp.src.utils.validator import validate_leave_request
import logging
import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification
import pickle
import os
import sys

# Projenin kök dizinini Python yoluna ekle
project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Model dosyalarının yolu
model_path = os.path.join(
    project_root, 'nlp', 'models', 'intent_classifier_model')
label_encoder_path = os.path.join(
    project_root, 'nlp', 'models', 'label_encoder.pkl')

# Model ve tokenizer'ı yükle
tokenizer = RobertaTokenizer.from_pretrained(model_path)
model = RobertaForSequenceClassification.from_pretrained(model_path)
model.eval()

# Label encoder'ı yükle
with open(label_encoder_path, 'rb') as f:
    le = pickle.load(f)


def normalize_entity(entity_type, value):
    if isinstance(value, list):
        return ' '.join([str(v) for v in value if v is not None])
    return str(value) if value is not None else ''


def classify_intent(text):
    logger.debug(f"Classifying intent for: {text}")
    entities = extract_entities(text)
    logger.debug(f"Extracted entities: {entities}")
    normalized_text = preprocess_text(text)
    logger.debug(f"Normalized text: {normalized_text}")

    inputs = tokenizer(normalized_text, return_tensors="pt",
                       truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    probabilities = torch.nn.functional.softmax(logits, dim=-1)
    confidence, predicted_class = torch.max(probabilities, dim=-1)

    # Increase the confidence threshold
    if confidence.item() < 0.6:
        intent = "unknown"
    else:
        intent = le.inverse_transform([predicted_class.item()])[0]

    logger.debug(
        f"Classified intent: {intent}, confidence: {confidence.item()}")
    return intent, confidence.item(), entities


def chatbot_response(intent, confidence, entities):
    if intent == "greeting":
        return "Merhaba! Size nasıl yardımcı olabilirim? Yıllık izin talebi, mazeret izni veya satın alma talebi gibi konularda size yardımcı olabilirim."
    elif intent in ["leave_request_annual", "confirm_annual_leave"]:
        return "Yıllık izin talebiniz için tarihleri alabilir miyim? Örneğin: 01.08.2024 ve 05.08.2024 arası"
    elif intent in ["leave_request_excuse", "confirm_excuse_leave"]:
        return "Mazeret izni talebiniz için tarih ve saatleri alabilir miyim? Örneğin: 05.08.2024 tarihi 09:30-11:30 arası"
    elif intent == "purchase_request":
        return "Satın alma talebiniz için detayları alabilir miyim? Örneğin: 10 adet A4 kağıt"
    elif intent == "unknown":
        return "Üzgünüm, ne demek istediğinizi tam olarak anlayamadım. Lütfen başka bir şekilde ifade eder misiniz?"
    else:
        return "Üzgünüm, bu konuda size yardımcı olamıyorum. Başka bir konuda yardımcı olabilir miyim?"


def process_message(text):
    logger.debug(f"Processing message: {text}")
    intent, confidence, entities = classify_intent(text)
    logger.debug(
        f"Intent: {intent}, Confidence: {confidence}, Entities: {entities}")

    if intent in ["confirm_annual_leave", "confirm_excuse_leave", "leave_request_annual", "leave_request_excuse"]:
        dates = entities.get("DATE", [])
        times = entities.get("TIME", [])
        start_date = dates[0] if dates else None
        end_date = dates[1] if len(dates) > 1 else start_date
        start_time = times[0] if times else None
        end_time = times[1] if len(times) > 1 else None

        logger.debug(f"Dates: {start_date}, {end_date}")
        logger.debug(f"Times: {start_time}, {end_time}")

        is_valid, message = validate_leave_request(
            start_date, end_date, start_time, end_time, None)
        if not is_valid:
            logger.debug(f"Invalid leave request: {message}")
            return intent, confidence, message, entities

    response = chatbot_response(intent, confidence, entities)
    logger.debug(f"Chatbot response: {response}")

    return str(intent), float(confidence), str(response), {k: [str(v) for v in vs] if isinstance(vs, list) else str(vs) for k, vs in entities.items()}
