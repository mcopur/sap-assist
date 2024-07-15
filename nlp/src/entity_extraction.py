import spacy
import re
from datetime import datetime
from utils.normalizer import normalize_entity
from utils.validator import validate_leave_request

nlp = spacy.load("tr_core_news_md")


def extract_entities(text):
    doc = nlp(text)
    entities = {
        "DATE": [],
        "TIME": [],
        "PERSON": [],
        "ORG": [],
        "DURATION": []
    }

    for ent in doc.ents:
        if ent.label_ in entities:
            normalized_value = normalize_entity(ent.label_, ent.text)
            if normalized_value:
                entities[ent.label_].append(normalized_value)

    # Özel tarih formatı için regex
    date_pattern = r'\d{2}[./]\d{2}[./]\d{4}'
    dates = re.findall(date_pattern, text)
    for date in dates:
        normalized_date = normalize_entity('DATE', date)
        if normalized_date:
            entities["DATE"].append(normalized_date)

    # Özel saat formatı için regex
    time_pattern = r'\d{2}:\d{2}'
    times = re.findall(time_pattern, text)
    for time in times:
        normalized_time = normalize_entity('TIME', time)
        if normalized_time:
            entities["TIME"].append(normalized_time)

    # Süre için regex
    duration_pattern = r'\d+\s*(saat|h|dakika|m)'
    durations = re.findall(duration_pattern, text, re.IGNORECASE)
    for duration in durations:
        normalized_duration = normalize_entity('DURATION', ' '.join(duration))
        if normalized_duration:
            entities["DURATION"].append(normalized_duration)

    return entities


def extract_leave_request_info(text):
    entities = extract_entities(text)

    start_date = entities["DATE"][0] if entities["DATE"] else None
    end_date = entities["DATE"][1] if len(entities["DATE"]) > 1 else None
    start_time = entities["TIME"][0] if entities["TIME"] else None
    end_time = entities["TIME"][1] if len(entities["TIME"]) > 1 else None
    duration = entities["DURATION"][0] if entities["DURATION"] else None

    is_valid, message = validate_leave_request(
        start_date, end_date, start_time, end_time, duration)

    return {
        "start_date": start_date,
        "end_date": end_date,
        "start_time": start_time,
        "end_time": end_time,
        "duration": duration,
        "person": entities["PERSON"][0] if entities["PERSON"] else None,
        "organization": entities["ORG"][0] if entities["ORG"] else None,
        "is_valid": is_valid,
        "validation_message": message
    }
