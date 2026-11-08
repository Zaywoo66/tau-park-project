#  TAU-PARK — Система бронирования глэмпинга

## Run with Docker Compose

The Compose stack starts PostgreSQL, the FastAPI API, and a separately served
React catalog. The current React catalog displays local sample houses; its
booking button is not wired to the API. Authentication and booking are available
through the API at `/docs`.

1. Copy `.env.example` to `.env`. Replace `POSTGRES_PASSWORD` with a URL-safe
   password and `SECRET_KEY` with a long random value. Keep `.env` private.
2. Run `docker compose config --quiet`, then `docker compose up --build --wait`.
3. Open the catalog at <http://localhost:8080> and API docs at
   <http://localhost:8000/docs>. If 8080 is occupied, set
   `TAU_FRONTEND_PORT` to a free port in `.env` and use that port instead.
4. `docker compose down` stops the stack and keeps the PostgreSQL volume.

These screenshots were captured from the running local Compose stack. The
catalog shows sample content; the API screenshot shows actual registered routes.

![TAU-PARK React catalog landing page](docs/screenshots/catalog-desktop.png)
![TAU-PARK FastAPI documentation with authentication and house routes](docs/screenshots/api-docs.png)

## Backend tests

CI runs the authentication and booking API tests against a disposable PostgreSQL
database named `tau_park_test`. The tests refuse any other database name. To run
them against a local Compose stack, create that database once with
`docker compose exec db sh -c 'createdb -U "$POSTGRES_USER" tau_park_test'`, install
`backend/requirements-test.txt` in a Python 3.12 virtual environment, set
`TEST_DATABASE_URL` to
`postgresql+asyncpg://<user>:<password>@127.0.0.1:5433/tau_park_test`
using your `.env` values, and run `python -m pytest -q backend/tests`. If 5433
is occupied, change `TAU_DB_PORT` in `.env` and use the same port in the test URL.
The CI workflow also builds and starts the documented Compose stack and checks
both HTTP endpoints.

The manual backend/frontend development instructions below remain available.

![React](https://img.shields.io/badge/react-19.0-blue?logo=react)
![TypeScript](https://img.shields.io/badge/typescript-5.x-blue?logo=typescript)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Async-316192?logo=postgresql)

**TAU-PARK** — учебный проект для бронирования глэмпинг-домиков. Backend предоставляет API для пользователей, домов и бронирований. Отдельный React-каталог пока показывает локальные примерные данные; его кнопка бронирования ещё не подключена к API.

##  Ключевые возможности

-  **Аутентификация и авторизация** — безопасная система входа на основе JWT (access & refresh токены).
-  **Каталог домиков** — демонстрационный React-интерфейс с локальными данными.
-  **Управление бронированиями** — создание, просмотр и отмена бронирований с проверкой доступности в реальном времени.
-  **Валидация данных** — строгая типизация и валидация на уровне API (Pydantic).
-  **Высокая производительность** — асинхронный бэкенд на FastAPI и SQLAlchemy.

##  Технологический стек

### Frontend (Клиентская часть)
- **Фреймворк:** React 19 + Vite
- **Язык:** TypeScript
- **Стилизация:** Tailwind CSS v4 + PostCSS
- **Линтинг:** ESLint

### Backend (Серверная часть)
- **Фреймворк:** FastAPI (Python 3)
- **База данных:** PostgreSQL (через `asyncpg`)
- **ORM:** SQLAlchemy (Async)
- **Безопасность:** Passlib (bcrypt), python-jose (JWT)
- **Сервер:** Uvicorn

##  Структура проекта

```text
tau-park-project/
├── backend/                # Исходный код серверной части (FastAPI)
│   ├── app/                # Основной код (routers, models, schemas, services)
│   ├── prisma/             # (Опционально) Конфигурация Prisma
│   └── requirements.txt    # Зависимости Python
├── frontend/               # Исходный код клиентской части (React)
│   ├── src/                # Компоненты, страницы, хуки
│   ├── public/             # Статические ресурсы
│   └── package.json        # Зависимости Node.js
├── run_backend.py          # Скрипт для быстрого запуска бэкенда из корня
└── .env                    # (Не в коммите) Переменные окружения
```

##  Быстрый старт (Установка и запуск)

### Требования
- **Node.js** (v18+)
- **Python** (v3.10+)
- **PostgreSQL** (установленный и запущенный сервер)

### 1. Настройка окружения
Создайте файл `.env` в **корневой папке проекта** (рядом с `run_backend.py`) со следующим содержимым:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/tau_park_db

# Security (JWT)
SECRET_KEY=your-super-secret-key-change-it-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

# CORS (опционально, по умолчанию разрешен localhost:5173)
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### 2. Запуск Backend (Серверная часть)

Откройте терминал в корневой директории проекта:

```bash
# Создание виртуального окружения
python -m venv venv

# Активация виртуального окружения
# Для Windows:
venv\Scripts\activate
# Для macOS/Linux:
source venv/bin/activate

# Установка зависимостей
pip install -r backend/requirements.txt

# Запуск сервера
python run_backend.py
```
> Бэкенд будет доступен по адресу: http://localhost:8000
> Интерактивная документация API (Swagger UI): http://localhost:8000/docs

### 3. Запуск Frontend (Клиентская часть)

Откройте новый терминал и перейдите в папку `frontend`:

```bash
cd frontend

# Установка зависимостей
npm install

# Запуск dev-сервера
npm run dev
```
> Фронтенд будет доступен по адресу: http://localhost:5173

##  API Endpoints (Краткий обзор)

Документация автоматически генерируется FastAPI и доступна в `/docs`. 
Основные группы маршрутов (`/api/...`):
- `/auth/` — Регистрация, логин, получение токенов.
- `/users/` — Управление профилями пользователей.
- `/houses/` — Получение списка домиков, добавление новых (для админов).
- `/bookings/` — Создание и управление бронированиями.

##  Лицензия

Проект проприетарный. Все права защищены.
