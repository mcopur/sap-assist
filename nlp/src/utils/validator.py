
# nlp/src/utils/validator.py
from datetime import datetime, timedelta
import holidays
import dateparser


def parse_date(date):
    if isinstance(date, str):
        try:
            return datetime.strptime(date, "%d.%m.%Y").date()
        except ValueError:
            try:
                return datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                return None
    elif isinstance(date, datetime):
        return date.date()
    return None


def validate_date(date_str):
    parsed_date = parse(date_str, languages=['tr'])
    
    if not parsed_date:
        return False, "Geçersiz tarih formatı. Lütfen geçerli bir tarih girin."
    
    today = datetime.now().date()
    
    if parsed_date.date() < today:
        return False, "Geçmiş tarihler için izin talebi oluşturamazsınız."
    
    max_future_date = today + timedelta(days=365)
    if parsed_date.date() > max_future_date:
        return False, "En fazla bir yıl ilerisine kadar izin talebi oluşturabilirsiniz."
    
    if parsed_date.weekday() >= 5:
        return False, "Hafta sonları için izin talebi oluşturamazsınız."
    
    tr_holidays = holidays.Turkey(years=parsed_date.year)
    if parsed_date.date() in tr_holidays:
        return False, f"{parsed_date.date()} tarihinde resmi tatil olduğu için izin talebi oluşturamazsınız."
    
    return True, parsed_date.strftime("%d.%m.%Y")

def validate_time(time):
    if time is None:
        return True, None  # Zaman belirtilmemişse geçerli kabul ediyoruz
    # Burada gerekirse saat doğrulaması yapabilirsiniz
    return True, None


def validate_duration(duration_minutes):
    if duration_minutes is None:
        return True, None  # Süre belirtilmemişse geçerli kabul ediyoruz
    if duration_minutes <= 0:
        return False, "Süre sıfırdan büyük olmalıdır."
    if duration_minutes > 480:  # 8 saat
        return False, "Bir günde en fazla 8 saatlik izin talep edebilirsiniz."
    return True, None


def validate_leave_request(start_date, end_date, start_time, end_time, duration):
    # Tarih kontrolü
    is_valid, message = validate_date(start_date)
    if not is_valid:
        return False, message

    parsed_start_date = parse_date(start_date)
    parsed_end_date = parse_date(end_date) if end_date else parsed_start_date

    if parsed_end_date:
        is_valid, message = validate_date(end_date)
        if not is_valid:
            return False, message
        if parsed_end_date < parsed_start_date:
            return False, "Bitiş tarihi başlangıç tarihinden önce olamaz."

    # Saat kontrolü
    is_valid, message = validate_time(start_time)
    if not is_valid:
        return False, message

    is_valid, message = validate_time(end_time)
    if not is_valid:
        return False, message

    # Süre kontrolü
    is_valid, message = validate_duration(duration)
    if not is_valid:
        return False, message

    # Tarih aralığı kontrolü
    if parsed_start_date and parsed_end_date:
        date_diff = (parsed_end_date - parsed_start_date).days
        if date_diff > 30:
            return False, "En fazla 30 günlük izin talep edebilirsiniz."

    return True, None
