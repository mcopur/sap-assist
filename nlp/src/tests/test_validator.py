# nlp/src/tests/test_validator.py

import unittest
from datetime import datetime, timedelta
from src.utils.validator import validate_date, validate_time, validate_duration, validate_leave_request


class TestValidator(unittest.TestCase):

    def test_validate_date(self):
        today = datetime.now().date()
        tomorrow = (today + timedelta(days=1)).strftime('%Y-%m-%d')
        yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        future = (today + timedelta(days=400)).strftime('%Y-%m-%d')

        self.assertTrue(validate_date(tomorrow)[0])
        self.assertFalse(validate_date(yesterday)[0])
        self.assertFalse(validate_date(future)[0])
        self.assertFalse(validate_date('invalid-date')[0])

    def test_validate_time(self):
        self.assertTrue(validate_time('14:30')[0])
        self.assertFalse(validate_time('25:00')[0])
        self.assertFalse(validate_time('invalid-time')[0])

    def test_validate_duration(self):
        self.assertTrue(validate_duration(240)[0])  # 4 saat
        self.assertFalse(validate_duration(0)[0])
        self.assertFalse(validate_duration(500)[0])  # 8 saatten fazla

    def test_validate_leave_request(self):
        today = datetime.now().date()
        tomorrow = (today + timedelta(days=1)).strftime('%Y-%m-%d')
        day_after = (today + timedelta(days=2)).strftime('%Y-%m-%d')

        # Geçerli izin talebi
        print("Valid leave request test")
        result = validate_leave_request(
            tomorrow, day_after, '09:00', '17:00', 480)
        print(f"Result: {result}")
        self.assertTrue(result[0])

        # Geçersiz tarih aralığı
        print("Invalid date range test")
        result = validate_leave_request(
            day_after, tomorrow, '09:00', '17:00', 480)
        print(f"Result: {result}")
        self.assertFalse(result[0])

        # Geçersiz saat aralığı
        print("Invalid time range test")
        result = validate_leave_request(
            tomorrow, day_after, '17:00', '09:00', 480)
        print(f"Result: {result}")
        self.assertFalse(result[0])

        # 29 gün (geçerli olmalı)
        print("29 days duration test")
        result = validate_leave_request(
            tomorrow, (today + timedelta(days=28)).strftime('%Y-%m-%d'), '09:00', '17:00', 480)
        print(f"Result: {result}")
        self.assertTrue(result[0])

        # 30 gün (geçersiz olmalı)
        print("30 days duration test")
        result = validate_leave_request(
            tomorrow, (today + timedelta(days=30)).strftime('%Y-%m-%d'), '09:00', '17:00', 480)
        print(f"Result: {result}")
        self.assertFalse(result[0])


if __name__ == '__main__':
    unittest.main()
