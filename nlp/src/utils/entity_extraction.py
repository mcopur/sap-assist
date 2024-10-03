import spacy
import logging

logger = logging.getLogger(__name__)

try:
    nlp = spacy.load("tr_core_news_md")
    logger.info("Successfully loaded Turkish language model (tr_core_news_md)")
except IOError:
    logger.error(
        "Couldn't load tr_core_news_md. Please ensure it's installed correctly.")
    nlp = None


def extract_entities(text):
    if nlp is None:
        logger.error("No language model available. Cannot extract entities.")
        return {}

    doc = nlp(text)
    entities = {
        "DATE": [],
        "TIME": [],
        "PERSON": [],
        "ORG": [],
    }

    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)

    return entities
