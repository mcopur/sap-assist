import logging

# ErrorLogger'ı oluştur
ErrorLogger = logging.getLogger('error_logger')
ErrorLogger.setLevel(logging.ERROR)

# Hata mesajlarını dosyaya yazmak için bir handler ekle
file_handler = logging.FileHandler('error.log')
file_handler.setLevel(logging.ERROR)

# Hata mesajlarının formatını belirle
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Handler'ı logger'a ekle
ErrorLogger.addHandler(file_handler)
