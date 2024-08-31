import logging
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from ..models.intent_classifier import IntentClassifier
from .entity_extraction import extract_entities
from .data_preprocessing import preprocess_text
from .validator import validate_leave_request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Chatbot:
    def __init__(self, intent_model_path, response_model_path):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.intent_classifier = IntentClassifier(intent_model_path)
        self.response_tokenizer = AutoTokenizer.from_pretrained(response_model_path)
        self.response_model = AutoModelForCausalLM.from_pretrained(response_model_path).to(self.device)

    def generate_response(self, intent, entities, context):
        prompt = f"Intent: {intent}\nEntities: {entities}\nContext: {context}\nResponse:"
        inputs = self.response_tokenizer(prompt, return_tensors="pt").to(self.device)
        
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
        
        response = self.response_tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.strip()

    def process_message(self, text, context=None):
        if context is None:
            context = {}

        logger.info(f"Processing message: {text}")

        preprocessed_text = preprocess_text(text)
        intent, confidence = self.intent_classifier.predict(preprocessed_text)
        entities = extract_entities(text)

        logger.info(f"Classified intent: {intent}, confidence: {confidence}")
        logger.info(f"Extracted entities: {entities}")

        if intent in ['confirm_annual_leave', 'confirm_excuse_leave']:
            is_valid, validation_message = validate_leave_request(entities, context)
            if not is_valid:
                response = validation_message
            else:
                response = self.generate_response(intent, entities, context)
        else:
            response = self.generate_response(intent, entities, context)

        context.update({
            'last_intent': intent,
            'last_entities': entities
        })

        return {
            'intent': intent,
            'confidence': confidence,
            'entities': entities,
            'response': response,
            'context': context
        }

    def refine_intent(self, intent, confidence, context):
        if confidence < 0.5:
            return "unknown"
        if context.get('awaiting_date_confirmation') and intent not in ['confirm_annual_leave', 'confirm_excuse_leave']:
            return 'confirm_annual_leave'
        return intent