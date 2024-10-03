import torch
from transformers import AutoTokenizer, BertForSequenceClassification
import pickle
from nlp.src.utils.entity_extraction import extract_entities
from nlp.src.utils.data_preprocessing import preprocess_text
import logging
import os

logger = logging.getLogger(__name__)


class Chatbot:
    def __init__(self, model_path, label_encoder_path):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = BertForSequenceClassification.from_pretrained(
                model_path).to(self.device)
            logger.info(f"Successfully loaded model from {model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self.tokenizer = None
            self.model = None

        try:
            with open(label_encoder_path, 'rb') as f:
                self.label_encoder = pickle.load(f)
            logger.info(
                f"Successfully loaded label encoder from {label_encoder_path}")
        except Exception as e:
            logger.error(f"Error loading label encoder: {str(e)}")
            self.label_encoder = None

    def classify_intent(self, text):
        if self.model is None or self.tokenizer is None or self.label_encoder is None:
            logger.error(
                "Model, tokenizer, or label encoder not initialized. Cannot classify intent.")
            return "unknown", 0.0

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

    def process_message(self, text):
        entities = extract_entities(text)
        intent, confidence = self.classify_intent(text)

        return {
            "intent": intent,
            "confidence": confidence,
            "entities": entities
        }
