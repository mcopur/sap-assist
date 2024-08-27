import spacy
import re
from dateparser import parse
import datetime

# Türkçe Spacy modelini yükle
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

    # Spacy'nin tanıdığı varlıkları çıkar
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)

    # Tarih çıkarma
    date_patterns = [
        r'\d{1,2}[./]\d{1,2}[./]\d{2,4}',
        r'\d{1,2}\s+(?:ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)\s+\d{4}',
        r'(?:pazartesi|salı|çarşamba|perşembe|cuma|cumartesi|pazar)',
        r'(?:bugün|yarın|dün|gelecek hafta|geçen hafta|önümüzdeki ay|gelecek ay)'
    ]

    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                parsed_date = parse(match, languages=['tr'])
                if parsed_date:
                    formatted_date = parsed_date.strftime("%Y-%m-%d")
                    if formatted_date not in entities["DATE"]:
                        entities["DATE"].append(formatted_date)
            except:
                pass

    # Saat çıkarma
    time_patterns = [
        r'\d{1,2}:\d{2}',
        r'sabah|öğlen|akşam|gece'
    ]
    for pattern in time_patterns:
        times = re.findall(pattern, text, re.IGNORECASE)
        entities["TIME"].extend(times)

    # Süre çıkarma
    duration_patterns = [
        r'(\d+)\s*(?:saat|gün|hafta|ay|yıl)',
        r'(\d+)\s*(?:s|g|h|a|y)'
    ]

    for pattern in duration_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            entities["DURATION"].append(match)

    # Kişi isimlerini çıkarma (eğer Spacy tarafından tanınmadıysa)
    if not entities["PERSON"]:
        for token in doc:
            if token.pos_ == "PROPN" and token.text not in [ent.text for ent in doc.ents]:
                entities["PERSON"].append(token.text)

    return entities


def normalize_entity(entity_type, value):
    if entity_type == "DATE":
        try:
            parsed_date = parse(value, languages=['tr'])
            if parsed_date:
                return parsed_date.strftime("%Y-%m-%d")
        except:
            pass
    elif entity_type == "TIME":
        try:
            parsed_time = parse(value, languages=['tr'])
            if parsed_time:
                return parsed_time.strftime("%H:%M")
        except:
            pass
    elif entity_type == "DURATION":
        # Süreyi standart bir formata dönüştür (örneğin, saat cinsinden)
        value = value.lower()
        if "saat" in value or "s" in value:
            return int(re.findall(r'\d+', value)[0])
        elif "gün" in value or "g" in value:
            return int(re.findall(r'\d+', value)[0]) * 24
        elif "hafta" in value or "h" in value:
            return int(re.findall(r'\d+', value)[0]) * 24 * 7
        elif "ay" in value or "a" in value:
            return int(re.findall(r'\d+', value)[0]) * 24 * 30
        elif "yıl" in value or "y" in value:
            return int(re.findall(r'\d+', value)[0]) * 24 * 365

    return value


def extract_leave_request_info(text):
    entities = extract_entities(text)

    start_date = entities["DATE"][0] if entities["DATE"] else None
    end_date = entities["DATE"][1] if len(entities["DATE"]) > 1 else start_date
    start_time = entities["TIME"][0] if entities["TIME"] else None
    end_time = entities["TIME"][1] if len(entities["TIME"]) > 1 else None
    duration = entities["DURATION"][0] if entities["DURATION"] else None

    return {
        "start_date": normalize_entity("DATE", start_date) if start_date else None,
        "end_date": normalize_entity("DATE", end_date) if end_date else None,
        "start_time": normalize_entity("TIME", start_time) if start_time else None,
        "end_time": normalize_entity("TIME", end_time) if end_time else None,
        "duration": normalize_entity("DURATION", duration) if duration else None,
        "person": entities["PERSON"][0] if entities["PERSON"] else None,
        "organization": entities["ORG"][0] if entities["ORG"] else None,
    }

# Test fonksiyonu


def test_entity_extraction():
    test_cases = [
        "Yarın saat 14:00'te 2 saatlik bir toplantım var.",
        "15 Ağustos 2024 tarihinden 20 Ağustos 2024 tarihine kadar yıllık izin almak istiyorum.",
        "Önümüzdeki Pazartesi ve Salı günleri için mazeret izni talep ediyorum.",
        "Ahmet Bey ile gelecek hafta Çarşamba günü öğleden sonra görüşmem var.",
        "Bu ay içinde 3 günlük bir eğitime katılacağım.",
    ]

    for case in test_cases:
        print(f"Test case: {case}")
        entities = extract_entities(case)
        print("Extracted entities:", entities)
        leave_info = extract_leave_request_info(case)
        print("Leave request info:", leave_info)
        print("---")


if __name__ == "__main__":
    test_entity_extraction()
