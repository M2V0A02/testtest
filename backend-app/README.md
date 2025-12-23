# Flask Backend Application

Простое Flask API приложение для демонстрации GitOps с ArgoCD.

## Endpoints

- `GET /api/info` - возвращает информацию о версии и конфигурации
- `GET /health` - health check endpoint

## Переменные окружения

- `APP_VERSION` - версия приложения (по умолчанию: v1.0)
- `APP_MESSAGE` - кастомное сообщение (по умолчанию: Hello from Flask Backend!)

## Сборка Docker образа

```bash
cd backend-app
docker build -t flask-backend:v1.0 .
docker tag flask-backend:v1.0 your-dockerhub-username/flask-backend:v1.0
docker push your-dockerhub-username/flask-backend:v1.0
```

## Локальный запуск

```bash
pip install -r requirements.txt
export APP_VERSION=v1.0
export APP_MESSAGE="Hello from local!"
python app.py
```

Приложение будет доступно на http://localhost:5000
