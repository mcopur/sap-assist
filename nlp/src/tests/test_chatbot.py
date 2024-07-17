import unittest
from src.chatbot.bot import Chatbot
from src.intent_recognition import classify_intent
from src.utils.validator import validate_leave_request


class MockModel:
    def __init__(self):
        pass


class TestChatbot(unittest.TestCase):
    def setUp(self):
        self.chatbot = Chatbot(MockModel(), None, {
                               'greeting': 0, 'leave_request': 1}, 'cpu')

    def test_greeting(self):
        response = self.chatbot.process_message("Merhaba")
        self.assertIn(response, ["Merhaba! Size nasıl yardımcı olabilirim?",
                                 "Hoş geldiniz! Bugün size nasıl yardımcı olabilirim?",
                                 "Selam! Nasıl yardımcı olabilirim?"])

    def test_leave_request(self):
        responses = [
            self.chatbot.process_message("İzin almak istiyorum"),
            self.chatbot.process_message("15/07/2024 ile 20/07/2024 arası")
        ]
        self.assertIn(
            "İzin talebinizi almak için size birkaç soru soracağım", responses[0])
        self.assertIn("İzin talebinizi aldım", responses[1])
        self.assertIn("15/07/2024", responses[1])
        self.assertIn("20/07/2024", responses[1])

    def test_invalid_date(self):
        responses = [
            self.chatbot.process_message("İzin almak istiyorum"),
            self.chatbot.process_message("32/13/2024")
        ]
        self.assertIn("Üzgünüm, girdiğiniz tarih geçersiz", responses[1])

    def test_feedback(self):
        feedback_request = self.chatbot.get_feedback()
        self.assertEqual(feedback_request,
                         "Bu yanıt yardımcı oldu mu? (Evet/Hayır)")

        positive_feedback = self.chatbot.process_feedback("Evet")
        self.assertIn("Teşekkür ederim!", positive_feedback)

        negative_feedback = self.chatbot.process_feedback("Hayır")
        self.assertIn("Üzgünüm, daha iyi yardımcı olamadım", negative_feedback)


if __name__ == '__main__':
    unittest.main()
