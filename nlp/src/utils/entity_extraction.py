import spacy
import re
from datetime import datetime

nlp = spacy.load("tr_core_news_md")  # Türkçe model


def extract_entities(text):
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

    # Ek tarih ve saat çıkarımı
    entities["DATE"].extend(extract_dates(text))
    entities["TIME"].extend(extract_time(text))

    return entities


def extract_dates(text):
    date_pattern = r'\d{1,2}[./]\d{1,2}[./]\d{2,4}'
    dates = re.findall(date_pattern, text)
    return dates


def extract_time(text):
    time_pattern = r'\d{1,2}:\d{2}'
    times = re.findall(time_pattern, text)
    return times
