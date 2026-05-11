# SEUGC System

Веб-система автоматической приоритизации обращений клиентов на базе `Django + DRF + Vue + PostgreSQL` с ML-инференсом при создании обращения.

## Что реализовано в MVP

- Регистрация и авторизация (JWT).
- Роли: `client`, `manager`.
- Создание обращения клиентом.
- Автоматический анализ текста при создании обращения:
  - приоритет `low/medium/high`;
  - тональность `negative/neutral/positive`;
  - вероятности по классам приоритета.
- Хранение обращения и результатов анализа в БД.
- Интерфейсы:
  - клиент: список своих обращений + создание;
  - менеджер: список всех обращений, фильтрация, сортировка, смена статуса;
  - карточка обращения.
- Единый JSON-формат API-ответов.
- Docker-конфигурация для быстрого запуска.

## Архитектура

- `backend/` — Django/DRF backend.
- `frontend/` — Vue 3 SPA.
- `backend_inference_bundle/` — предоставленный ML bundle.

ML-интеграция реализована через сервис:

- `apps/ml/service.py`: `analyze_ticket(text) -> { priority, sentiment }`.
- При наличии bundle и зависимостей используется `InferenceCoordinator` из `backend_inference_bundle/inference_dual_models.py`.
- Если bundle или heavy-зависимости недоступны, автоматически включается rule-based fallback (чтобы API продолжал работать).

## API endpoints

Базовый префикс: `/api`

Auth:

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `GET /api/auth/me/`

Tickets:

- `POST /api/tickets/` — создать обращение (client)
- `GET /api/tickets/my/` — список своих обращений (client)
- `GET /api/tickets/manager/` — список всех обращений (manager)
- `GET /api/tickets/{id}/` — карточка обращения
- `PATCH /api/tickets/{id}/status/` — смена статуса (manager)
- `POST /api/analyze/` — ручной вызов анализа текста (debug)

## Локальный запуск (без Docker)

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env  # на Linux/macOS: cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Backend будет доступен на `http://localhost:8000`.

Опционально для полного ML-контура:

```bash
pip install -r requirements-ml.txt
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend будет доступен на `http://localhost:5173`.

## Тесты

Backend-тесты запускаются из директории `backend` с тестовыми настройками (`SQLite in-memory`):

```bash
cd backend
python manage.py test --settings=config.settings.test -v 2
```

Дополнительная проверка конфигурации backend:

```bash
python manage.py check --settings=config.settings.test
```

## Запуск через Docker

```bash
docker compose up --build
```

Сервисы:

- frontend: `http://localhost:5173`
- backend: `http://localhost:8000`
- postgres: `localhost:5432`

## Роли и доступ

- Клиент может создавать обращения и видеть только свои.
- Менеджер видит все обращения, фильтрует/сортирует и меняет статус.
- `superuser` автоматически получает роль `manager`.

## Формат ответа API

Успех:

```json
{
  "success": true,
  "data": {}
}
```

Ошибка:

```json
{
  "success": false,
  "error": {
    "message": "Request failed.",
    "details": {}
  }
}
```
