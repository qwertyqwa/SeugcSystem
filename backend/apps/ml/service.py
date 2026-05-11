from __future__ import annotations

import contextlib
import importlib.util
import io
import logging
import sys
import threading
from pathlib import Path
from typing import Dict


logger = logging.getLogger(__name__)
_analyzer_instance = None
_analyzer_lock = threading.Lock()


class KeywordOverrideManager:
    _urgent_fragments = {
        "срочно",
        "критич",
        "авар",
        "немедлен",
        "outage",
        "urgent",
        "critical",
        "полностью останов",
        "все встало",
        "риск срыва",
    }
    _negative_fragments = {
        "не можем",
        "не могу",
        "недоволен",
        "ужас",
        "плохо",
        "злой",
        "пизд",
        "бляд",
        "хуй",
        "ебан",
    }
    _escalation_fragments = {
        "не работает",
        "не функционирует",
        "не запускается",
        "проблема",
        "ошибка",
        "все встало",
        "полностью останов",
    }
    _polite_fragments = {
        "спасибо",
        "признател",
        "пожалуйста",
        "коллеги",
        "добрый день",
        "буду благодар",
    }

    def _contains_any(self, prepared_text: str, fragments: set[str]) -> bool:
        return any(fragment in prepared_text for fragment in fragments)

    def apply(self, text: str, result: Dict[str, object]) -> Dict[str, object]:
        prepared = (text or "").lower()
        priority = result.get("priority", {}) if isinstance(result, dict) else {}
        sentiment = result.get("sentiment", {}) if isinstance(result, dict) else {}

        has_urgent_signal = self._contains_any(prepared, self._urgent_fragments)
        if has_urgent_signal:
            priority["label"] = "high"
            probabilities = priority.get("probabilities", {}) or {}
            probabilities["low"] = 0.03
            probabilities["medium"] = 0.07
            probabilities["high"] = 0.9
            priority["probabilities"] = probabilities
            priority["score"] = max(float(priority.get("score", 0.0)), float(probabilities["high"]))

        has_negative_signal = self._contains_any(prepared, self._negative_fragments)
        has_escalation_signal = self._contains_any(prepared, self._escalation_fragments)
        has_polite_signal = self._contains_any(prepared, self._polite_fragments)
        low_confidence_neutral = sentiment.get("label") == "neutral" and float(sentiment.get("score", 0.0)) < 0.7
        should_force_negative = has_negative_signal or (has_urgent_signal and has_escalation_signal)
        if should_force_negative or (low_confidence_neutral and not has_polite_signal):
            sentiment["label"] = "negative"
            sentiment["score"] = max(float(sentiment.get("score", 0.0)), 0.84)

        return {
            "priority": priority,
            "sentiment": sentiment,
        }


@contextlib.contextmanager
def _suppress_library_output():
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        yield


class FallbackAnalyzer:
    _high_keywords = {
        "\u0441\u0440\u043e\u0447\u043d\u043e",
        "\u0430\u0432\u0430\u0440\u0438\u044f",
        "\u0441\u043b\u043e\u043c\u0430\u043b\u043e\u0441\u044c",
        "\u043a\u0440\u0438\u0442\u0438\u0447\u043d\u043e",
        "critical",
        "urgent",
        "fail",
        "outage",
    }
    _medium_keywords = {
        "\u043e\u0448\u0438\u0431\u043a\u0430",
        "\u043f\u0440\u043e\u0431\u043b\u0435\u043c\u0430",
        "\u043d\u0435 \u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442",
        "issue",
        "bug",
        "delay",
    }
    _negative_keywords = {
        "\u0443\u0436\u0430\u0441\u043d\u043e",
        "\u043f\u043b\u043e\u0445\u043e",
        "\u043d\u0435\u0434\u043e\u0432\u043e\u043b\u0435\u043d",
        "\u0437\u043b\u043e\u0439",
        "angry",
        "bad",
        "hate",
    }
    _negative_fragments = {
        "\u043d\u0430\u0445",
        "\u0445\u0443\u0439",
        "\u043f\u0438\u0437\u0434",
        "\u0431\u043b\u044f\u0434",
        "\u0435\u0431\u0430\u043d",
        "\u0435\u0431\u043b",
        "\u0437\u0430\u0435\u0431",
        "\u043e\u0445\u0440\u0435\u043d",
        "\u043d\u0438\u0445\u0443\u044f",
        "\u0434\u0435\u0431\u0438\u043b",
        "\u043f\u0440\u043e\u0432\u0430\u043b",
        "\u043d\u0435 \u043c\u043e\u0433\u0443",
        "\u043d\u0435 \u043c\u043e\u0436\u0435\u043c",
        "\u043d\u0435 \u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442",
        "\u043d\u0435 \u0444\u0443\u043d\u043a\u0446\u0438\u043e\u043d\u0438\u0440\u0443\u0435\u0442",
        "\u0432\u0441\u0435 \u0432\u0441\u0442\u0430\u043b\u043e",
        "\u043f\u0430\u0440\u0430\u043b\u0438\u0437",
    }
    _positive_keywords = {
        "\u0441\u043f\u0430\u0441\u0438\u0431\u043e",
        "\u0445\u043e\u0440\u043e\u0448\u043e",
        "\u043e\u0442\u043b\u0438\u0447\u043d\u043e",
        "\u0434\u043e\u0432\u043e\u043b\u0435\u043d",
        "great",
        "thanks",
        "good",
        "love",
    }

    def _contains_keyword(self, prepared_text: str, keywords: set[str]) -> bool:
        return any(keyword in prepared_text for keyword in keywords)

    def _contains_fragment(self, prepared_text: str, fragments: set[str]) -> bool:
        return any(fragment in prepared_text for fragment in fragments)

    def analyze_ticket(self, text: str) -> Dict[str, object]:
        prepared = (text or "").lower()

        if self._contains_keyword(prepared, self._high_keywords):
            priority = "high"
            probs = {"low": 0.05, "medium": 0.15, "high": 0.8}
        elif self._contains_keyword(prepared, self._medium_keywords):
            priority = "medium"
            probs = {"low": 0.2, "medium": 0.65, "high": 0.15}
        else:
            priority = "low"
            probs = {"low": 0.75, "medium": 0.2, "high": 0.05}

        if self._contains_keyword(prepared, self._negative_keywords) or self._contains_fragment(
            prepared, self._negative_fragments
        ):
            sentiment = "negative"
            sentiment_score = 0.82
        elif self._contains_keyword(prepared, self._positive_keywords):
            sentiment = "positive"
            sentiment_score = 0.82
        else:
            sentiment = "neutral"
            sentiment_score = 0.7

        return {
            "priority": {
                "label": priority,
                "score": probs[priority],
                "probabilities": probs,
            },
            "sentiment": {
                "label": sentiment,
                "score": sentiment_score,
            },
        }


class BundleAnalyzer:
    _priority_map = {
        "low": "low",
        "medium": "medium",
        "high": "high",
        "\u043d\u0438\u0437\u043a\u0438\u0439": "low",
        "\u0441\u0440\u0435\u0434\u043d\u0438\u0439": "medium",
        "\u0432\u044b\u0441\u043e\u043a\u0438\u0439": "high",
    }
    _sentiment_map = {
        "negative": "negative",
        "neutral": "neutral",
        "positive": "positive",
        "label_0": "negative",
        "label_1": "neutral",
        "label_2": "positive",
        "\u043d\u0435\u0433\u0430\u0442\u0438\u0432\u043d\u0430\u044f": "negative",
        "\u043d\u0435\u0439\u0442\u0440\u0430\u043b\u044c\u043d\u0430\u044f": "neutral",
        "\u043f\u043e\u0437\u0438\u0442\u0438\u0432\u043d\u0430\u044f": "positive",
    }

    def __init__(self, coordinator_class):
        self._coordinator = coordinator_class()
        self._override_manager = KeywordOverrideManager()

    def _normalize_priority_label(self, label: str) -> str:
        return self._priority_map.get(str(label).strip().lower(), "medium")

    def _normalize_sentiment_label(self, label: str) -> str:
        return self._sentiment_map.get(str(label).strip().lower(), "neutral")

    def analyze_ticket(self, text: str) -> Dict[str, object]:
        raw = self._coordinator.analyze_text(text)
        raw_priority = raw.get("priority", {}) if isinstance(raw, dict) else {}
        raw_sentiment = raw.get("sentiment", {}) if isinstance(raw, dict) else {}

        priority_label = self._normalize_priority_label(raw_priority.get("label", "medium"))
        priority_probs = raw_priority.get("probabilities", {}) or {}
        normalized_probs = {
            "low": float(priority_probs.get("low", 0.0)),
            "medium": float(priority_probs.get("medium", 0.0)),
            "high": float(priority_probs.get("high", 0.0)),
        }

        if sum(normalized_probs.values()) == 0:
            normalized_probs[priority_label] = 1.0

        sentiment_source = raw_sentiment.get("label_raw") or raw_sentiment.get("label", "neutral")
        sentiment_label = self._normalize_sentiment_label(sentiment_source)

        result = {
            "priority": {
                "label": priority_label,
                "score": float(raw_priority.get("score", normalized_probs.get(priority_label, 0.0))),
                "probabilities": normalized_probs,
            },
            "sentiment": {
                "label": sentiment_label,
                "score": float(raw_sentiment.get("score", 0.0)),
            },
        }
        return self._override_manager.apply(text, result)


def _load_bundle_coordinator():
    bundle_file = Path(__file__).resolve().parents[3] / "backend_inference_bundle" / "inference_dual_models.py"
    if not bundle_file.exists():
        logger.warning("ML bundle file was not found: %s", bundle_file)
        return None

    spec = importlib.util.spec_from_file_location("bundle_inference_dual_models", str(bundle_file))
    if spec is None or spec.loader is None:
        logger.warning("Could not load ML bundle spec from %s", bundle_file)
        return None

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    with _suppress_library_output():
        spec.loader.exec_module(module)
    return getattr(module, "InferenceCoordinator", None)


def _create_analyzer():
    coordinator_class = None
    try:
        coordinator_class = _load_bundle_coordinator()
    except Exception as error:
        logger.warning("Failed to load ML bundle coordinator, fallback enabled: %s", error)

    if coordinator_class is None:
        return FallbackAnalyzer()

    try:
        with _suppress_library_output():
            return BundleAnalyzer(coordinator_class)
    except Exception as error:
        logger.warning("ML coordinator initialization failed, fallback enabled: %s", error)
        return FallbackAnalyzer()


def get_analyzer():
    global _analyzer_instance
    if _analyzer_instance is None:
        with _analyzer_lock:
            if _analyzer_instance is None:
                _analyzer_instance = _create_analyzer()
    return _analyzer_instance


def analyze_ticket(text: str) -> Dict[str, object]:
    return get_analyzer().analyze_ticket(text)
