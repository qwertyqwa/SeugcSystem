from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    pipeline,
)

try:
    import joblib
except Exception:  # pragma: no cover
    joblib = None


@dataclass
class PriorityPrediction:
    label: str
    score: float
    probabilities: Dict[str, float]


@dataclass
class SentimentPrediction:
    label_raw: str
    label: str
    score: float


class SentimentModelManager:
    def __init__(self, model_name: str, device: str) -> None:
        self._label_map = {
            "negative": "негативная",
            "neutral": "нейтральная",
            "positive": "позитивная",
            "LABEL_0": "негативная",
            "LABEL_1": "нейтральная",
            "LABEL_2": "позитивная",
        }
        self._pipe = pipeline(
            task="text-classification",
            model=model_name,
            tokenizer=model_name,
            device=0 if device == "cuda" else -1,
        )

    def predict(self, text: str) -> SentimentPrediction:
        result = self._pipe(text, truncation=True, max_length=256)[0]
        raw = result["label"]
        return SentimentPrediction(
            label_raw=raw,
            label=self._label_map.get(raw, raw),
            score=float(result["score"]),
        )


class PriorityTransformerManager:
    def __init__(self, model_path_or_name: str, device: str) -> None:
        self._device = device
        self._tokenizer = AutoTokenizer.from_pretrained(model_path_or_name, use_fast=False)
        self._model = AutoModelForSequenceClassification.from_pretrained(model_path_or_name)
        self._model.eval()
        if self._device == "cuda":
            self._model.cuda()

    def predict(self, text: str) -> PriorityPrediction:
        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=256,
        )
        if self._device == "cuda":
            inputs = {k: v.cuda() for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self._model(**inputs)

        probs = torch.softmax(outputs.logits, dim=1)[0].detach().cpu().tolist()
        id2label = self._model.config.id2label or {0: "low", 1: "medium", 2: "high"}
        pred_id = int(torch.argmax(outputs.logits, dim=1).item())
        labels = [id2label.get(i, str(i)) for i in range(len(probs))]
        prob_map = {labels[i]: float(probs[i]) for i in range(len(probs))}

        return PriorityPrediction(
            label=labels[pred_id],
            score=float(probs[pred_id]),
            probabilities=prob_map,
        )


class PrioritySklearnManager:
    def __init__(self, model_path: Path) -> None:
        if joblib is None:
            raise RuntimeError("joblib not installed, cannot load sklearn model")
        self._model = joblib.load(str(model_path))

    def predict(self, text: str) -> PriorityPrediction:
        pred_label = self._model.predict([text])[0]
        score = 0.0
        probabilities: Dict[str, float] = {}

        if hasattr(self._model, "decision_function"):
            decision = self._model.decision_function([text])[0]
            if hasattr(decision, "tolist"):
                raw_values = decision.tolist()
                if isinstance(raw_values, float):
                    raw_values = [raw_values]
                labels = ["low", "medium", "high"][: len(raw_values)]
                normalized = torch.softmax(torch.tensor(raw_values), dim=0).tolist()
                probabilities = {labels[i]: float(normalized[i]) for i in range(len(normalized))}
                if str(pred_label) in probabilities:
                    score = probabilities[str(pred_label)]

        return PriorityPrediction(
            label=str(pred_label),
            score=float(score),
            probabilities=probabilities,
        )


class PriorityZeroShotManager:
    def __init__(self, model_name: str, device: str) -> None:
        self._labels = ["low", "medium", "high"]
        self._pipe = pipeline(
            task="zero-shot-classification",
            model=model_name,
            device=0 if device == "cuda" else -1,
        )

    def predict(self, text: str) -> PriorityPrediction:
        out = self._pipe(
            text,
            candidate_labels=self._labels,
            multi_label=False,
            hypothesis_template="This text has {} priority.",
        )
        label = out["labels"][0]
        score = float(out["scores"][0])
        probabilities = {
            out["labels"][idx]: float(out["scores"][idx]) for idx in range(len(out["labels"]))
        }
        return PriorityPrediction(label=label, score=score, probabilities=probabilities)


class InferenceCoordinator:
    def __init__(
        self,
        priority_local_transformer_path: str = "models/priority",
        priority_local_svc_path: str = "models/linear_svc_tfidf_best.joblib",
        priority_zeroshot_name: str = "MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli",
        sentiment_name: str = "cointegrated/rubert-tiny-sentiment-balanced",
    ) -> None:
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        self._sentiment = SentimentModelManager(sentiment_name, self._device)
        self._priority = self._build_priority_model(
            priority_local_transformer_path,
            priority_local_svc_path,
            priority_zeroshot_name,
        )

    def _build_priority_model(
        self,
        transformer_path: str,
        svc_path: str,
        zeroshot_name: str,
    ):
        transformer_dir = Path(transformer_path)
        svc_file = Path(svc_path)

        if transformer_dir.exists():
            return PriorityTransformerManager(str(transformer_dir), self._device)
        if svc_file.exists():
            return PrioritySklearnManager(svc_file)
        return PriorityZeroShotManager(zeroshot_name, self._device)

    def analyze_text(self, text: str) -> Dict[str, object]:
        sentiment = self._sentiment.predict(text)
        priority = self._priority.predict(text)
        return {
            "text": text,
            "sentiment": sentiment.__dict__,
            "priority": priority.__dict__,
        }

    def analyze_batch(self, texts: List[str]) -> List[Dict[str, object]]:
        return [self.analyze_text(text) for text in texts]
