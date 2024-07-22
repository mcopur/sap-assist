from datetime import datetime, timedelta


def validate_date(date):
    if date is None:
        return False, "Tarih belirtilmemiş."

    if not isinstance(date, datetime):
        try:
            date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return False, "Geçersiz tarih formatı. Lütfen YYYY-MM-DD formatında bir tarih girin."

    if date < datetime.now().date():
        return False, "Geçmiş tarihler için izin talebi oluşturamazsınız."
    if date > datetime.now().date() + timedelta(days=365):
        return False, "En fazla bir yıl ilerisine kadar izin talebi oluşturabilirsiniz."
    return True, None


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

    if end_date:
        is_valid, message = validate_date(end_date)
        if not is_valid:
            return False, message
        if end_date < start_date:
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
    if start_date and end_date:
        date_diff = (end_date - start_date).days
        if date_diff > 30:
            return False, "En fazla 30 günlük izin talep edebilirsiniz."

    return True, None
