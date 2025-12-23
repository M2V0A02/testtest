# Argo CD Test Repository

Этот репозиторий содержит тестовое приложение для демонстрации работы Argo CD.

## Структура

- `k8s/test-app/` - Kubernetes манифесты для тестового приложения (nginx)
  - `deployment.yaml` - Deployment с 2 репликами nginx
  - `service.yaml` - Service для доступа к приложению

## Использование с Argo CD

Для деплоя приложения через Argo CD используйте путь: `k8s/test-app`
