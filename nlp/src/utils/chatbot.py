import os
import torch
import pickle
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForCausalLM
from nlp.src.utils.entity_extraction import extract_entities
from nlp.src.utils.data_preprocessing import preprocess_text
import logging

logger = logging.getLogger(__name__)


class Chatbot:
    def __init__(self, intent_model_path, response_model_path):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")

        logger.info(f"Loading intent model from {intent_model_path}")
        self.intent_tokenizer = AutoTokenizer.from_pretrained(
            intent_model_path, local_files_only=True)
        self.intent_model = AutoModelForSequenceClassification.from_pretrained(
            intent_model_path, local_files_only=True).to(self.device)

        logger.info(f"Loading response model from {response_model_path}")
        self.response_tokenizer = AutoTokenizer.from_pretrained(
            response_model_path, local_files_only=True)
        self.response_model = AutoModelForCausalLM.from_pretrained(
            response_model_path, local_files_only=True).to(self.device)

        # Label encoder'ı yükle
        label_encoder_path = os.path.join(os.path.dirname(
            intent_model_path), '..', 'label_encoder.pkl')
        logger.info(f"Loading label encoder from {label_encoder_path}")
        with open(label_encoder_path, 'rb') as f:
            self.label_encoder = pickle.load(f)

    def process_message(self, text):
        logger.debug(f"Processing message: {text}")
        preprocessed_text = preprocess_text(text)

        inputs = self.intent_tokenizer(
            preprocessed_text, return_tensors="pt", truncation=True, padding=True).to(self.device)
        with torch.no_grad():
            outputs = self.intent_model(**inputs)

        logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        confidence, predicted_class = torch.max(probabilities, dim=-1)

        intent = self.label_encoder.inverse_transform(
            [predicted_class.item()])[0]
        confidence = confidence.item()

        entities = extract_entities(text)

        response = self.generate_response(intent, entities, text)

        logger.debug(
            f"Processed message. Intent: {intent}, Confidence: {confidence}, Entities: {entities}")
        return intent, confidence, response, entities

    def generate_response(self, intent, entities, original_text):
        # Basit bir yanıt oluşturma
        return f"Anladım, intent: {intent}, entities: {entities}, original text: {original_text}"
