# ArgoCD GitOps Demo Repository

Репозиторий для тестирования и изучения GitOps практик с ArgoCD.

## Что внутри

### 1. Микросервисное приложение (Основной проект)

**Backend:** Flask API
- Простой REST API эндпоинт `/api/info`
- Конфигурируется через ConfigMap
- Health checks и readiness probes

**Frontend:** Nginx + HTML
- Красивая страница с градиентным дизайном
- Подключается к backend API через fetch
- Показывает версию, сообщение и hostname backend pod

**GitOps:** ArgoCD Application
- Автоматическая синхронизация из git
- Self-healing (откат ручных изменений)
- Sync waves (правильный порядок деплоя)

### 2. Тестовое приложение (Legacy)

Простое nginx приложение для первых экспериментов с ArgoCD.

## Структура проекта

```
argo-cd/
├── backend-app/              # Flask приложение
│   ├── app.py               # Flask API код
│   ├── requirements.txt     # Python зависимости
│   ├── Dockerfile           # Docker образ
│   └── README.md
├── frontend-app/             # Frontend на nginx
│   ├── index.html           # HTML страница с UI
│   ├── nginx.conf           # Nginx конфигурация
│   └── Dockerfile
├── k8s/
│   ├── microservices/        # Kubernetes манифесты для микросервисов
│   │   ├── backend/
│   │   │   ├── configmap.yaml
│   │   │   ├── deployment.yaml
│   │   │   └── service.yaml
│   │   └── frontend/
│   │       ├── configmap.yaml
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       ├── html-configmap.yaml
│   │       └── nginx-configmap.yaml
│   └── test-app/             # Legacy тестовое приложение
│       ├── deployment.yaml
│       └── service.yaml
├── argocd-microservices-app.yaml  # ArgoCD Application для микросервисов
├── argocd-app.yaml                # ArgoCD Application для demo
├── argocd-app-local.yaml          # Шаблон для локального репозитория
├── QUICKSTART.md                  # Быстрый старт
├── GITOPS-TESTING.md              # Подробные тестовые сценарии
└── INSTRUCTIONS.md                # Инструкции по ArgoCD

```

## Быстрый старт

### Шаг 1: Запушить на GitHub

```bash
git add .
git commit -m "Add GitOps microservices demo"
git remote add origin https://github.com/YOUR_USERNAME/argo-cd.git
git push -u origin master
```

### Шаг 2: Обновить URL в манифесте

Отредактируйте `argocd-microservices-app.yaml`:
```yaml
source:
  repoURL: https://github.com/YOUR_USERNAME/argo-cd.git  # ← Замените на свой
```

### Шаг 3: Развернуть в ArgoCD

```bash
kubectl apply -f argocd-microservices-app.yaml
```

### Шаг 4: Проверить

```bash
# Статус
~/.local/bin/argocd app get microservices-app

# Pods
kubectl get pods -n default

# Port-forward для доступа
kubectl port-forward svc/frontend 8081:80 -n default
```

Откройте: http://localhost:8081

## GitOps Тестовые сценарии

Протестируйте следующие GitOps возможности:

1. **Автоматическая синхронизация** - измените ConfigMap в git
2. **Self-healing** - вручную измените replicas в кластере
3. **Pruning** - удалите ресурс из git
4. **Rollback** - откат через git history
5. **Sync waves** - правильный порядок деплоя
6. **Health checks** - сломайте приложение и посмотрите статус

Подробные инструкции: `GITOPS-TESTING.md`

## ArgoCD доступ

```
URL:      https://localhost:8080
Username: admin
Password: 2jCE1952fifemCft
```

## Что тестируется

- ✅ Декларативная конфигурация в git
- ✅ Автоматическая синхронизация
- ✅ Self-healing
- ✅ Pruning неиспользуемых ресурсов
- ✅ Sync waves для правильного порядка
- ✅ Health checks и статусы
- ✅ Rollback через git
- ✅ ConfigMaps для конфигурации
- ✅ Multi-replica deployments
- ✅ Liveness и Readiness probes

## Документация

- `QUICKSTART.md` - Быстрый старт за 5 минут
- `GITOPS-TESTING.md` - 7 детальных тестовых сценариев
- `INSTRUCTIONS.md` - Инструкции по ArgoCD CLI и UI

## Архитектура

```
┌─────────────┐        ┌──────────────┐
│   GitHub    │───────▶│   ArgoCD     │
│   (Git)     │        │   Server     │
└─────────────┘        └──────┬───────┘
                              │
                              │ Sync
                              ▼
                       ┌──────────────┐
                       │  Kubernetes  │
                       │   Cluster    │
                       └──────┬───────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
         ┌────▼────┐                    ┌────▼────┐
         │ Backend │                    │Frontend │
         │ (Flask) │◀───────────────────│ (Nginx) │
         │ 2 pods  │   HTTP /api/info   │ 2 pods  │
         └─────────┘                    └─────────┘
```

## Полезные команды

```bash
# Проверить статус приложения
~/.local/bin/argocd app get microservices-app

# Форсировать синхронизацию
~/.local/bin/argocd app sync microservices-app

# Посмотреть логи
kubectl logs -l app=backend -f
kubectl logs -l app=frontend -f

# Откатить через ArgoCD
~/.local/bin/argocd app rollback microservices-app <revision>

# Удалить приложение
~/.local/bin/argocd app delete microservices-app
```

## Следующие шаги

1. Пройдите все сценарии из `GITOPS-TESTING.md`
2. Добавьте базу данных (Redis/PostgreSQL)
3. Настройте multi-environment (dev/staging/prod) с Kustomize
4. Добавьте pre-sync и post-sync hooks
5. Интегрируйте CI/CD pipeline

Happy GitOps! 🚀
