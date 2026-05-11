# Backend inference bundle

Этот пакет сделан для быстрого прогона двух моделей:
- приоритет (`low` / `medium` / `high`);
- тональность (`negative` / `neutral` / `positive`).

## Что внутри

- `inference_dual_models.py` — единый инференс для двух моделей.
- `run_test_20.py` — тестовый прогон по 20 фрагментам.
- `test_fragments_20.csv` — входные тестовые фрагменты.
- `requirements.txt` — зависимости.

## Как выбирается модель приоритета

1. Если есть `models/priority` — берется локальная transformer-модель.
2. Если нет, но есть `models/linear_svc_tfidf_best.joblib` — берется локальная SVC.
3. Если нет ни того ни другого — fallback на zero-shot модель из Hugging Face.

## Запуск теста

Из папки bundle:

`python run_test_20.py`

На выходе появится файл `test_results_20.csv`.

## Важно

В текущем проекте не найден локальный файл SVC (`.joblib`) и полноценные веса локальной transformer-модели.
Поэтому без добавления локальных весов будет использован fallback (zero-shot для приоритета и HF-модель для тональности).
