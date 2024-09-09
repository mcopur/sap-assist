import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, GPT2Tokenizer, GPT2LMHeadModel
import json
import os


class Chatbot:
    def __init__(self, intent_model_path, response_model_path, label_encoder_path):
        self.intent_tokenizer = AutoTokenizer.from_pretrained(
            intent_model_path)
        self.intent_model = AutoModelForSequenceClassification.from_pretrained(
            intent_model_path)
        self.intent_model.eval()

        self.response_tokenizer = GPT2Tokenizer.from_pretrained(
            response_model_path)
        self.response_model = GPT2LMHeadModel.from_pretrained(
            response_model_path)
        self.response_model.eval()

        with open(label_encoder_path, 'r') as f:
            self.intent_labels = json.load(f)

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        self.intent_model.to(self.device)
        self.response_model.to(self.device)

    def classify_intent(self, text):
        inputs = self.intent_tokenizer(
            text, return_tensors="pt", truncation=True, padding=True).to(self.device)
        with torch.no_grad():
            outputs = self.intent_model(**inputs)

        logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        confidence, predicted_class = torch.max(probabilities, dim=-1)

        intent = self.intent_labels[predicted_class.item()]
        return intent, confidence.item()

    def generate_response(self, intent, entities):
        input_text = f"Intent: {intent}\nContext: {json.dumps(entities)}\nResponse:"
        input_ids = self.response_tokenizer.encode(
            input_text, return_tensors="pt").to(self.device)

        with torch.no_grad():
            output = self.response_model.generate(
                input_ids, max_length=150, num_return_sequences=1, no_repeat_ngram_size=2)

        response = self.response_tokenizer.decode(
            output[0], skip_special_tokens=True)
        return response.split("Response:")[-1].strip()

    def process_message(self, message):
        intent, confidence = self.classify_intent(message)
        # Bu fonksiyonu implement etmeniz gerekecek
        entities = self.extract_entities(message)
        response = self.generate_response(intent, entities)
        return intent, confidence, response, entities

    def extract_entities(self, message):
        # Bu fonksiyonu, varlık çıkarımı için implement etmeniz gerekecek
        # Şimdilik boş bir sözlük döndürüyoruz
        return {}

# Chatbot'u başlatmak için kullanılacak fonksiyon


class defaultLabelEncoder:
    def __init__(self):
        self.classes_ = ["greeting", "leave_request_annual",
                         "leave_request_excuse", "purchase_request", "unknown"]

    def inverse_transform(self, indices):
        return [self.classes_[i] for i in indices]


def initialize_chatbot():
    project_root = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', '..'))
    model_path = os.path.join(project_root, 'models',
                              'intent_classifier_model')
    le_path = os.path.join(project_root, 'models', 'label_encoder.pkl')
    return Chatbot(model_path, le_path)
