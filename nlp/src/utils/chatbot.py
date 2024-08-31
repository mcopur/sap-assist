# nlp/src/utils/chatbot.py

import logging
from ..models.intent_classifier import IntentClassifier
from ..models.entity_extractor import EntityExtractor
from ..models.response_generator import ResponseGenerator
from .data_preprocessing import preprocess_text
from .validator import validate_leave_request

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Chatbot:
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.response_generator = ResponseGenerator()

    def process_message(self, text, context=None):
        logger.debug(f"Processing message: {text}")

        if context is None:
            context = {}

        preprocessed_text = preprocess_text(text)
        intent, confidence = self.intent_classifier.classify(preprocessed_text)
        entities = self.entity_extractor.extract(preprocessed_text)
        logger.debug(
            f"Intent: {intent}, Confidence: {confidence}, Entities: {entities}")

        intent = self.refine_intent(intent, confidence, context)

        response = self.response_generator.generate(intent, entities, context)

        if intent in ['confirm_annual_leave', 'confirm_excuse_leave']:
            is_valid, message = validate_leave_request(entities, context)
            if not is_valid:
                response = message

        context['last_intent'] = intent

        return intent, confidence, response, entities

    def refine_intent(self, intent, confidence, context):
        if context.get('awaiting_date_confirmation') and intent != 'confirm_annual_leave':
            return 'confirm_annual_leave'
        return intent
