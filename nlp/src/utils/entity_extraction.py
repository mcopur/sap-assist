import spacy
import logging
from dateparser import parse
from datetime import datetime, timedelta

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

    # Tarih çıkarımı için ek işlem
    potential_date = parse(text, languages=['tr'])
    if potential_date:
        formatted_date = potential_date.strftime("%Y-%m-%d")
        entities["DATE"].append(formatted_date)

    return entities


def extract_date_range(text):
    words = text.lower().split()
    current_date = datetime.now()

    # Spesifik tarih formatlarını kontrol et
    date_formats = ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y']
    dates = []
    for word in words:
        for fmt in date_formats:
            try:
                date = datetime.strptime(word, fmt)
                dates.append(date.strftime('%Y-%m-%d'))
            except ValueError:
                pass

    if len(dates) == 2:
        return dates[0], dates[1]

    # Eğer spesifik tarihler bulunamazsa, diğer ifadeleri kontrol et
    if "hafta" in words:
        if "bu" in words:
            start = current_date
            end = start + timedelta(days=6)
        elif "gelecek" in words or "önümüzdeki" in words:
            start = current_date + timedelta(days=7)
            end = start + timedelta(days=6)
        else:
            return None, None

        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    if "ay" in words:
        if "bu" in words:
            start = current_date.replace(day=1)
            end = (start + timedelta(days=32)
                   ).replace(day=1) - timedelta(days=1)
        elif "gelecek" in words or "önümüzdeki" in words:
            start = (current_date.replace(day=1) +
                     timedelta(days=32)).replace(day=1)
            end = (start + timedelta(days=32)
                   ).replace(day=1) - timedelta(days=1)
        elif any(month in words for month in ["ocak", "şubat", "mart", "nisan", "mayıs", "haziran", "temmuz", "ağustos", "eylül", "ekim", "kasım", "aralık"]):
            parsed_date = parse(text, languages=['tr'])
            if parsed_date:
                start = parsed_date.replace(day=1)
                end = (start + timedelta(days=32)
                       ).replace(day=1) - timedelta(days=1)
                return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
        else:
            return None, None

        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    # Genel tarih ifadelerini kontrol et
    parsed_date = parse(text, languages=['tr'])
    if parsed_date:
        return parsed_date.strftime("%Y-%m-%d"), (parsed_date + timedelta(days=1)).strftime("%Y-%m-%d")

    return None, None
