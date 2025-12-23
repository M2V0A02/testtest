# Быстрый старт: GitOps с ArgoCD

## Что создано

**Backend:** Flask API с эндпоинтом `/api/info`
- Возвращает версию, сообщение и hostname
- Конфигурируется через ConfigMap
- 2 реплики с health checks

**Frontend:** Nginx со статической HTML страницей
- Красивый UI с градиентом
- Делает fetch к backend API
- Показывает версию и информацию

**ArgoCD Application:** Автоматическая синхронизация из git
- Self-healing включен
- Pruning включен
- Sync waves (backend → frontend)

## Структура

```
backend-app/          # Flask код и Dockerfile
frontend-app/         # HTML, nginx конфиг и Dockerfile
k8s/microservices/    # Kubernetes манифесты
  backend/            # ConfigMap, Deployment, Service
  frontend/           # ConfigMap, Deployment, Service, HTML
argocd-microservices-app.yaml  # ArgoCD Application
```

## Быстрый старт

### 1. Запушить на GitHub

```bash
# Создайте репозиторий на GitHub
git add .
git commit -m "Add GitOps microservices demo"
git remote add origin https://github.com/YOUR_USERNAME/argo-cd.git
git push -u origin master
```

### 2. Обновить URL репозитория

Отредактируйте `argocd-microservices-app.yaml`:
```yaml
source:
  repoURL: https://github.com/YOUR_USERNAME/argo-cd.git  # ← Замените
```

### 3. Развернуть в ArgoCD

```bash
kubectl apply -f argocd-microservices-app.yaml
```

### 4. Проверить статус

```bash
~/.local/bin/argocd app get microservices-app
kubectl get pods -n default
```

### 5. Открыть frontend

```bash
kubectl port-forward svc/frontend 8081:80 -n default
```

Откройте: http://localhost:8081

## Тестовые сценарии

Подробные инструкции в файле `GITOPS-TESTING.md`

**Быстрый тест Self-Healing:**
```bash
# Вручную измените количество реплик
kubectl scale deployment backend --replicas=5 -n default

# Подождите 10 секунд - ArgoCD откатит изменения
kubectl get pods -l app=backend
```

**Быстрый тест GitOps workflow:**
```bash
# Измените версию в ConfigMap
vim k8s/microservices/backend/configmap.yaml
# Поменяйте APP_VERSION: "v2.0"

git add k8s/microservices/backend/configmap.yaml
git commit -m "Update to v2.0"
git push

# Подождите 3 минуты или форсируйте синхронизацию
~/.local/bin/argocd app sync microservices-app

# Обновите страницу - версия изменится!
```

## ArgoCD UI

```
URL: https://localhost:8080
User: admin
Pass: 2jCE1952fifemCft
```

## Что дальше?

1. Пройдите все тесты из `GITOPS-TESTING.md`
2. Попробуйте изменить сообщения, цвета, количество реплик
3. Добавьте базу данных (Redis/PostgreSQL)
4. Настройте multi-environment с Kustomize

Удачи с GitOps! 🚀
