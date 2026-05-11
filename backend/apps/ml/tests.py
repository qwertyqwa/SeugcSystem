from django.test import TestCase

from .service import FallbackAnalyzer, KeywordOverrideManager


class FallbackAnalyzerTests(TestCase):
    def test_detects_high_priority_and_negative_sentiment(self):
        analyzer = FallbackAnalyzer()

        result = analyzer.analyze_ticket("Срочно: сервис сломалось, клиенты злой и недоволен")

        self.assertEqual(result["priority"]["label"], "high")
        self.assertEqual(result["sentiment"]["label"], "negative")
        self.assertGreater(result["priority"]["probabilities"]["high"], 0.7)

    def test_detects_low_priority_and_positive_sentiment(self):
        analyzer = FallbackAnalyzer()

        result = analyzer.analyze_ticket("Спасибо, все отлично и good")

        self.assertEqual(result["priority"]["label"], "low")
        self.assertEqual(result["sentiment"]["label"], "positive")
        self.assertGreater(result["sentiment"]["score"], 0.8)


class KeywordOverrideManagerTests(TestCase):
    def test_forces_high_and_negative_for_urgent_negative_text(self):
        manager = KeywordOverrideManager()
        source = {
            "priority": {
                "label": "medium",
                "score": 0.68,
                "probabilities": {"low": 0.2, "medium": 0.68, "high": 0.12},
            },
            "sentiment": {
                "label": "neutral",
                "score": 0.48,
            },
        }

        result = manager.apply(
            "Критический инцидент, срочно! Не работает, мы не можем начать работу, я недоволен.",
            source,
        )

        self.assertEqual(result["priority"]["label"], "high")
        self.assertEqual(result["sentiment"]["label"], "negative")
        self.assertGreaterEqual(result["priority"]["probabilities"]["high"], 0.9)
        self.assertGreaterEqual(result["sentiment"]["score"], 0.84)

    def test_keeps_polite_outage_text_neutral_without_urgent_escalation(self):
        manager = KeywordOverrideManager()
        source = {
            "priority": {
                "label": "medium",
                "score": 0.67,
                "probabilities": {"low": 0.19, "medium": 0.67, "high": 0.14},
            },
            "sentiment": {
                "label": "neutral",
                "score": 0.48,
            },
        }

        result = manager.apply(
            "Коллеги, привет! Буду признателен за помощь, первая конфигурация не работает. Спасибо.",
            source,
        )

        self.assertEqual(result["priority"]["label"], "medium")
        self.assertEqual(result["sentiment"]["label"], "neutral")
