# nlp/src/utils/entity_extraction.py
import spacy
import re
import dateparser
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
    # Türkçe ay isimleri
    tr_months = r"(ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)"

    # Tarih formatları için regex
    date_patterns = [
        r'\d{1,2}\s+' + tr_months + r'\s+\d{4}',  # 11 Ağustos 2024
        r'\d{1,2}[./-]\d{1,2}[./-]\d{4}',  # 11.08.2024 veya 11/08/2024
        r'\d{4}[./-]\d{1,2}[./-]\d{1,2}'   # 2024.08.11 veya 2024/08/11
    ]

    dates = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):  # Ay isimli formatlar için
                match = " ".join(match)
            date = parse(match, languages=['tr'])
            if date:
                dates.append(date.strftime('%d.%m.%Y'))

    return list(set(dates))  # Tekrar eden tarihleri kaldır


def extract_time(text):
    time_pattern = r'\d{1,2}:\d{2}'
    times = re.findall(time_pattern, text)
    return times  # datetime nesnesine dönüştürme işlemini kaldırdık


def extract_leave_request_info(text):
    entities = extract_entities(text)

    start_date = entities["DATE"][0] if entities["DATE"] else None
    end_date = entities["DATE"][1] if len(entities["DATE"]) > 1 else start_date
    start_time = entities["TIME"][0] if entities["TIME"] else None
    end_time = entities["TIME"][1] if len(entities["TIME"]) > 1 else None

    return {
        "start_date": start_date,
        "end_date": end_date,
        "start_time": start_time,
        "end_time": end_time,
        "person": entities["PERSON"][0] if entities["PERSON"] else None,
        "organization": entities["ORG"][0] if entities["ORG"] else None,
    }
