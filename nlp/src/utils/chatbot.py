import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import logging
from nlp.src.utils.entity_extraction import extract_entities, extract_leave_request_info
import pickle
import os

# Logging ayarları
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Model ve tokenizer yükleme
project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..'))
model_path = os.path.join(project_root, 'nlp', 'models',
                          'improved_intent_classifier_model')

# Tokenizer'ı yükle
if os.path.exists(os.path.join(model_path, 'tokenizer_config.json')):
    tokenizer = AutoTokenizer.from_pretrained(
        model_path, local_files_only=True)
else:
    tokenizer = AutoTokenizer.from_pretrained("dbmdz/bert-base-turkish-cased")

# Model'i yükle
if os.path.exists(os.path.join(model_path, 'pytorch_model.bin')):
    model = AutoModelForSequenceClassification.from_pretrained(
        model_path, local_files_only=True)
else:
    model = AutoModelForSequenceClassification.from_pretrained(
        "dbmdz/bert-base-turkish-cased")

model.eval()

# Label encoder'ı yükleme
le_path = os.path.join(project_root, 'nlp', 'models', 'label_encoder.pkl')
if os.path.exists(le_path):
    with open(le_path, 'rb') as f:
        le = pickle.load(f)
else:
    logger.warning("Label encoder file not found. Using dummy encoder.")
    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    le.classes_ = ['unknown']  # Dummy class

CONFIDENCE_THRESHOLD = 0.7


def classify_intent(text):
    logger.debug(f"Classifying intent for: {text}")
    inputs = tokenizer(text, return_tensors="pt",
                       truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    confidence, predicted_class = torch.max(probabilities, dim=-1)

    confidence = confidence.item()

    if confidence < CONFIDENCE_THRESHOLD:
        logger.debug(
            f"Low confidence: {confidence}. Returning unknown intent.")
        return "unknown", confidence

    intent = le.inverse_transform([predicted_class.item()])[0]

    # Basit kural tabanlı düzeltmeler
    if "yıllık izin" in text.lower():
        intent = "leave_request_annual"
        logger.debug(f"Rule-based correction: Changed intent to {intent}")

    logger.debug(f"Classified intent: {intent}, confidence: {confidence}")
    return intent, confidence


def generate_response(intent, entities, leave_info):
    if intent == "greeting":
        return "Merhaba! Size nasıl yardımcı olabilirim? Yıllık izin, mazeret izni veya satın alma talebi gibi konularda size yardımcı olabilirim."

    elif intent in ["leave_request_annual", "confirm_annual_leave"]:
        if leave_info['start_date'] and leave_info['end_date']:
            return f"{leave_info['start_date']} tarihinden {leave_info['end_date']} tarihine kadar yıllık izin talebinizi aldım. Başka bir detay eklemek ister misiniz?"
        elif leave_info['start_date']:
            return f"{leave_info['start_date']} tarihinden itibaren yıllık izin talebinizi aldım. Bitiş tarihi belirtmek ister misiniz?"
        else:
            return "Yıllık izin talebiniz için hangi tarihleri düşünüyorsunuz?"

    elif intent in ["leave_request_excuse", "confirm_excuse_leave"]:
        if leave_info['start_date'] and leave_info['start_time']:
            return f"{leave_info['start_date']} tarihinde saat {leave_info['start_time']} için mazeret izni talebinizi aldım. Onay için yöneticinize ileteceğim."
        elif leave_info['start_date']:
            return f"{leave_info['start_date']} tarihi için mazeret izni talebinizi aldım. Saat belirtmek ister misiniz?"
        else:
            return "Mazeret izni için tarih ve mümkünse saat belirtmeniz gerekiyor. Lütfen detayları paylaşır mısınız?"

    elif intent == "purchase_request":
        return "Satın alma talebiniz için lütfen ürün adı, miktar ve tahmini maliyeti belirtir misiniz?"

    else:
        return "Üzgünüm, talebinizi tam olarak anlayamadım. Lütfen daha açık bir şekilde ifade eder misiniz?"


def process_message(text, context=None):
    logger.debug(f"Processing message: {text}")

    intent, confidence = classify_intent(text)
    entities = extract_entities(text)
    leave_info = extract_leave_request_info(text)

    logger.debug(f"Intent: {intent}, Confidence: {confidence}")
    logger.debug(f"Entities: {entities}")
    logger.debug(f"Leave info: {leave_info}")

    if intent == "unknown":
        response = "Üzgünüm, ne demek istediğinizi tam olarak anlayamadım. Lütfen daha açık bir şekilde ifade eder misiniz?"
    elif context and context.get('last_intent') == "leave_request_annual" and intent == "confirm_annual_leave":
        # Tarih belirtme olarak kabul et
        intent = "date_specification"
        response = "Anladım, bu tarihi yıllık izin talebiniz için kaydediyorum. Başka bir şey eklemek ister misiniz?"
    else:
        response = generate_response(intent, entities, leave_info)

    logger.debug(f"Generated response: {response}")

    return intent, confidence, response, entities
