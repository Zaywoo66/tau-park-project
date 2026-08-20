"""
run_backend.py
==============
Точка запуска FastAPI бэкенда из корня проекта (tau-park-project/).

Что делает этот скрипт:
  1. Добавляет папку `backend/` в sys.path, чтобы все импорты вида
     `from app.config import ...` внутри backend/app/ работали корректно.
  2. Запускает uvicorn программно — без необходимости вручную задавать
     переменную окружения PYTHONPATH каждый раз.

Использование:
    python run_backend.py
    python run_backend.py --port 8080
"""
import sys
from pathlib import Path

# Добавляем `backend/` в начало sys.path.
# После этого `import app` будет находить `backend/app/`.
BACKEND_DIR = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        # reload_dirs ограничивает слежение только папкой бэкенда —
        # иначе uvicorn будет перезапускаться при изменениях во frontend.
        reload_dirs=[str(BACKEND_DIR)],
    )
