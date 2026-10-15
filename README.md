#  TAU-PARK — Система бронирования глэмпинга

![React](https://img.shields.io/badge/react-19.0-blue?logo=react)
![TypeScript](https://img.shields.io/badge/typescript-5.x-blue?logo=typescript)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Async-316192?logo=postgresql)

**TAU-PARK** — учебный full-stack проект для бронирования домиков. Сейчас frontend показывает статический каталог, а backend предоставляет отдельный API для пользователей, домов и бронирований. Оформление бронирования через интерфейс пока не подключено.

##  Ключевые возможности

-  **Аутентификация и авторизация** — безопасная система входа на основе JWT (access & refresh токены).
-  **Каталог домиков** — статические карточки домиков в интерфейсе; API каталога реализован отдельно.
-  **Управление бронированиями через API** — создание, просмотр и отмена с проверкой пересечения дат.
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
Скопируйте `.env.example` в `.env` в корне проекта, затем задайте рабочий адрес PostgreSQL и случайный `SECRET_KEY`. Пример значений:

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
