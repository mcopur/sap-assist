from nlp.src.utils.entity_extraction import extract_entities
from transformers import AutoTokenizer, AutoModelForSequenceClassification, BertForMaskedLM
import torch
import logging
from flask import Flask, request, jsonify
import os
import sys

# Proje kök dizinini Python yoluna ekle
project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)


logger = logging.getLogger(__name__)


class Chatbot:
    def __init__(self, intent_model_path, response_model_path):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")

        # Intent Classification Model
        self.intent_tokenizer = AutoTokenizer.from_pretrained(
            intent_model_path)
        self.intent_model = AutoModelForSequenceClassification.from_pretrained(
            intent_model_path).to(self.device)

        # Response Generation Model
        self.response_tokenizer = AutoTokenizer.from_pretrained(
            response_model_path)
        self.response_model = BertForMaskedLM.from_pretrained(
            response_model_path).to(self.device)

    def classify_intent(self, text):
        inputs = self.intent_tokenizer(
            text, return_tensors="pt", truncation=True, padding=True).to(self.device)
        with torch.no_grad():
            outputs = self.intent_model(**inputs)

        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
        predicted_class = torch.argmax(probabilities, dim=-1).item()
        confidence = probabilities[0][predicted_class].item()

        intent = self.intent_model.config.id2label[predicted_class]
        return intent, confidence

    def generate_response(self, intent, entities, context):
        prompt = f"Intent: {intent}\nEntities: {entities}\nContext: {context}\nResponse:"
        inputs = self.response_tokenizer(
            prompt, return_tensors="pt", truncation=True, padding=True).to(self.device)

        with torch.no_grad():
            outputs = self.response_model.generate(
                **inputs,
                max_length=150,
                num_return_sequences=1,
                no_repeat_ngram_size=2,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.7
            )

        response = self.response_tokenizer.decode(
            outputs[0], skip_special_tokens=True)
        return response.strip()

    def process_message(self, text, context):
        logger.info(f"Processing message: {text}")

        intent, confidence = self.classify_intent(text)
        entities = extract_entities(text)

        logger.info(f"Classified intent: {intent}, confidence: {confidence}")
        logger.info(f"Extracted entities: {entities}")

        response = self.generate_response(intent, entities, context)

        result = {
            'intent': intent,
            'confidence': confidence,
            'entities': entities,
            'response': response,
            'context': context
        }

        return result
