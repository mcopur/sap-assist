# nlp/src/utils/nlp_utils.py
import spacy

nlp = spacy.load("en_core_web_sm")


def tokenize(text):
    doc = nlp(text)
    return [token.text for token in doc]


def get_entities(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]


def get_pos_tags(text):
    doc = nlp(text)
    return [(token.text, token.pos_) for token in doc]
