import re
from datetime import datetime


def normalize_date(date_string):
    """
    Farklı formatlardaki tarih girişlerini standart bir formata dönüştürür.
    Örnek: '15.07.2024', '15/07/2024', '2024-07-15' -> '2024-07-15'
    """
    if isinstance(date_string, list):
        date_string = date_string[0] if date_string else ""

    date_formats = ['%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d']
    for date_format in date_formats:
        try:
            return datetime.strptime(date_string, date_format).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return date_string  # Eğer hiçbir format uymuyorsa, orijinal string'i döndür


def normalize_time(time_string):
    """
    Farklı formatlardaki saat girişlerini standart bir formata dönüştürür.
    Örnek: '14:30', '14.30', '2:30 PM' -> '14:30'
    """
    if isinstance(time_string, list):
        time_string = time_string[0] if time_string else ""

    time_formats = ['%H:%M', '%H.%M', '%I:%M %p']
    for time_format in time_formats:
        try:
            return datetime.strptime(time_string, time_format).strftime('%H:%M')
        except ValueError:
            continue
    return time_string  # Eğer hiçbir format uymuyorsa, orijinal string'i döndür


def normalize_duration(duration_string):
    """
    Süre girişlerini dakika cinsinden standart bir formata dönüştürür.
    Örnek: '2 saat', '2h', '120 dakika', '120m' -> 120
    """
    if isinstance(duration_string, list):
        duration_string = duration_string[0] if duration_string else ""

    duration_pattern = r'(\d+)\s*(saat|h|dakika|m)'
    match = re.match(duration_pattern, duration_string, re.IGNORECASE)
    if match:
        value, unit = match.groups()
        if unit.lower() in ['saat', 'h']:
            return int(value) * 60
        else:
            return int(value)
    return duration_string  # Eğer pattern uymuyorsa, orijinal string'i döndür


def normalize_entity(entity_type, value):
    if isinstance(value, list):
        return ' '.join([str(v) for v in value if v is not None])
    return str(value) if value is not None else ''
