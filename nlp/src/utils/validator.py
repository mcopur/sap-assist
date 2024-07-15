
from datetime import datetime, timedelta


def validate_date(date_str):
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        if date < datetime.now().date():
            return False, "Geçmiş tarihler için izin talebi oluşturamazsınız."
        return True, None
    except ValueError:
        return False, "Geçersiz tarih formatı. Lütfen 'YYYY-MM-DD' formatında bir tarih girin."


def validate_time(time_str):
    try:
        time = datetime.strptime(time_str, '%H:%M').time()
        return True, None
    except ValueError:
        return False, "Geçersiz saat formatı. Lütfen 'HH:MM' formatında bir saat girin."


def validate_duration(duration_minutes):
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

    if end_date:
        is_valid, message = validate_date(end_date)
        if not is_valid:
            return False, message
        if end_date < start_date:
            return False, "Bitiş tarihi başlangıç tarihinden önce olamaz."

    # Saat kontrolü
    if start_time:
        is_valid, message = validate_time(start_time)
        if not is_valid:
            return False, message

    if end_time:
        is_valid, message = validate_time(end_time)
        if not is_valid:
            return False, message
        if start_time and end_time < start_time:
            return False, "Bitiş saati başlangıç saatinden önce olamaz."

    # Süre kontrolü
    if duration:
        is_valid, message = validate_duration(duration)
        if not is_valid:
            return False, message

    # Tarih aralığı kontrolü
    if start_date and end_date:
        date_diff = (datetime.strptime(end_date, '%Y-%m-%d') -
                     datetime.strptime(start_date, '%Y-%m-%d')).days
        if date_diff > 30:
            return False, "En fazla 30 günlük izin talep edebilirsiniz."

    return True, None
