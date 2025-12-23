# GitOps Тестирование с ArgoCD

Это руководство поможет вам протестировать основные возможности GitOps с помощью ArgoCD.

## Структура проекта

```
argo-cd/
├── backend-app/              # Flask приложение
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend-app/             # Frontend на nginx
│   ├── index.html
│   ├── nginx.conf
│   └── Dockerfile
├── k8s/microservices/        # Kubernetes манифесты
│   ├── backend/
│   │   ├── configmap.yaml
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   └── frontend/
│       ├── configmap.yaml
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── html-configmap.yaml
│       └── nginx-configmap.yaml
└── argocd-microservices-app.yaml  # ArgoCD Application
```

## Шаг 1: Подготовка репозитория

### 1.1 Запушить код на GitHub

```bash
# Создайте репозиторий на GitHub (например: your-username/argo-cd)
# Затем:
git add .
git commit -m "Add microservices app for GitOps testing"
git remote add origin https://github.com/YOUR_USERNAME/argo-cd.git
git push -u origin master
```

### 1.2 Обновить ArgoCD Application манифест

Отредактируйте `argocd-microservices-app.yaml` и замените `YOUR_USERNAME` на ваш GitHub username:

```yaml
source:
  repoURL: https://github.com/YOUR_USERNAME/argo-cd.git
```

## Шаг 2: Развернуть приложение в ArgoCD

### 2.1 Применить ArgoCD Application

```bash
kubectl apply -f argocd-microservices-app.yaml
```

### 2.2 Проверить статус приложения

В UI:
```
https://localhost:8080
```

Или через CLI:
```bash
~/.local/bin/argocd app list
~/.local/bin/argocd app get microservices-app
```

### 2.3 Дождаться синхронизации

ArgoCD автоматически:
1. Склонирует ваш репозиторий
2. Применит манифесты из `k8s/microservices/`
3. Создаст ConfigMaps, Deployments и Services
4. Использует sync waves (сначала backend, потом frontend)

```bash
# Проверить pods
kubectl get pods -n default

# Проверить services
kubectl get svc -n default
```

## Шаг 3: Доступ к приложению

### 3.1 Port-forward для frontend

```bash
kubectl port-forward svc/frontend 8081:80 -n default
```

### 3.2 Открыть в браузере

```
http://localhost:8081
```

Вы должны увидеть красивую страницу с информацией от backend API.

### 3.3 Проверить backend напрямую

```bash
kubectl port-forward svc/backend 5000:5000 -n default

# В другом терминале:
curl http://localhost:5000/api/info
```

## Шаг 4: Тестовые сценарии GitOps

### Сценарий 1: Изменение версии через ConfigMap

**Цель:** Проверить, что ArgoCD автоматически синхронизирует изменения из git.

1. Отредактируйте `k8s/microservices/backend/configmap.yaml`:
   ```yaml
   data:
     APP_VERSION: "v2.0"  # Было v1.0
     APP_MESSAGE: "Updated via GitOps! Version 2.0"
   ```

2. Закоммитьте и запушьте:
   ```bash
   git add k8s/microservices/backend/configmap.yaml
   git commit -m "Update backend to v2.0"
   git push
   ```

3. Наблюдайте за синхронизацией:
   ```bash
   # ArgoCD обнаружит изменения в течение ~3 минут
   ~/.local/bin/argocd app get microservices-app --refresh

   # Или форсировать синхронизацию:
   ~/.local/bin/argocd app sync microservices-app
   ```

4. Проверьте результат:
   - Обновите страницу frontend (http://localhost:8081)
   - Версия должна измениться на v2.0
   - Сообщение должно обновиться

**Ожидаемое поведение:**
- ArgoCD автоматически применит новый ConfigMap
- Pods будут перезапущены (если требуется)
- Изменения появятся в UI

---

### Сценарий 2: Изменение количества реплик

**Цель:** Проверить масштабирование через git.

1. Отредактируйте `k8s/microservices/backend/deployment.yaml`:
   ```yaml
   spec:
     replicas: 3  # Было 2
   ```

2. Закоммитьте и запушьте:
   ```bash
   git add k8s/microservices/backend/deployment.yaml
   git commit -m "Scale backend to 3 replicas"
   git push
   ```

3. Проверьте:
   ```bash
   kubectl get pods -n default -l app=backend -w
   ```

4. Обновите страницу несколько раз - hostname должен меняться (load balancing между 3 pods)

**Ожидаемое поведение:**
- ArgoCD создаст дополнительный pod
- Всего будет 3 backend pods

---

### Сценарий 3: Self-Healing (Восстановление)

**Цель:** Проверить, что ArgoCD восстанавливает ручные изменения в кластере.

1. Вручную измените что-то в кластере:
   ```bash
   kubectl scale deployment backend --replicas=5 -n default
   ```

2. Проверьте pods:
   ```bash
   kubectl get pods -n default -l app=backend
   # Увидите 5 pods
   ```

3. Подождите ~5-10 секунд. ArgoCD обнаружит drift (расхождение с git) и автоматически откатит изменения:
   ```bash
   kubectl get pods -n default -l app=backend
   # Вернется к 3 pods (или 2, если не делали Сценарий 2)
   ```

4. В ArgoCD UI увидите событие "Synced" - приложение было восстановлено.

**Ожидаемое поведение:**
- Self-healing откатит ручные изменения
- Кластер всегда соответствует git
- В логах ArgoCD будет видно событие восстановления

---

### Сценарий 4: Удаление ресурса (Pruning)

**Цель:** Проверить, что ArgoCD удаляет ресурсы, которых больше нет в git.

1. Удалите frontend ConfigMap из git:
   ```bash
   git rm k8s/microservices/frontend/configmap.yaml
   git commit -m "Remove frontend configmap (test pruning)"
   git push
   ```

2. ArgoCD автоматически удалит ConfigMap из кластера:
   ```bash
   kubectl get configmap frontend-config -n default
   # Error: configmap "frontend-config" not found
   ```

3. Верните файл обратно:
   ```bash
   git revert HEAD
   git push
   ```

**Ожидаемое поведение:**
- ArgoCD удалит ресурсы, которых нет в git (благодаря `prune: true`)
- При возврате файла, ConfigMap будет пересоздан

---

### Сценарий 5: Rollback через Git

**Цель:** Откатить приложение на предыдущую версию через git history.

1. Посмотрите историю коммитов:
   ```bash
   git log --oneline
   ```

2. Допустим, хотите откатиться на 2 коммита назад:
   ```bash
   git revert HEAD~2..HEAD
   git push
   ```

3. ArgoCD автоматически синхронизирует старую версию.

**Альтернатива - откат через ArgoCD:**
```bash
# Посмотреть историю
~/.local/bin/argocd app history microservices-app

# Откатиться на конкретную ревизию
~/.local/bin/argocd app rollback microservices-app <revision-id>
```

**Ожидаемое поведение:**
- Приложение откатится на предыдущую версию
- Все изменения применятся автоматически

---

### Сценарий 6: Sync Waves (Порядок деплоя)

**Цель:** Проверить, что ресурсы деплоятся в правильном порядке.

1. Удалите приложение:
   ```bash
   ~/.local/bin/argocd app delete microservices-app
   ```

2. Пересоздайте:
   ```bash
   kubectl apply -f argocd-microservices-app.yaml
   ```

3. Наблюдайте за порядком создания:
   ```bash
   kubectl get pods -n default -w
   ```

**Ожидаемое поведение:**
- Сначала создаются backend ресурсы (sync-wave: "1")
- Затем frontend ресурсы (sync-wave: "2")
- Это гарантирует, что backend готов до запуска frontend

---

### Сценарий 7: Проверка Health Status

**Цель:** Убедиться, что ArgoCD правильно определяет здоровье приложения.

1. Сломайте приложение - укажите несуществующий образ:
   ```yaml
   # k8s/microservices/backend/deployment.yaml
   containers:
   - name: backend
     image: python:99.99.99-nonexistent  # Несуществующий образ
   ```

2. Закоммитьте и запушьте:
   ```bash
   git add k8s/microservices/backend/deployment.yaml
   git commit -m "Break backend (test health check)"
   git push
   ```

3. Проверьте статус в ArgoCD:
   - В UI приложение будет показано как "Degraded" или "Progressing"
   - Pods не смогут запуститься (ImagePullBackOff)

4. Исправьте:
   ```bash
   git revert HEAD
   git push
   ```

**Ожидаемое поведение:**
- ArgoCD определит, что приложение нездорово
- Health checks покажут проблемы
- После исправления статус вернется к "Healthy"

---

## Шаг 5: Мониторинг и логи

### ArgoCD UI
```
https://localhost:8080
```

### ArgoCD CLI
```bash
# Статус приложения
~/.local/bin/argocd app get microservices-app

# Логи синхронизации
~/.local/bin/argocd app logs microservices-app

# События
kubectl get events -n default --sort-by='.lastTimestamp'
```

### Логи приложений
```bash
# Backend
kubectl logs -n default -l app=backend -f

# Frontend
kubectl logs -n default -l app=frontend -f
```

---

## Частые проблемы и решения

### Проблема: ArgoCD не видит изменения в git

**Решение:**
```bash
# Форсировать обновление
~/.local/bin/argocd app get microservices-app --refresh

# Или изменить настройки опроса (по умолчанию 3 минуты)
~/.local/bin/argocd app set microservices-app --sync-policy automated --self-heal
```

### Проблема: Pods не перезапускаются при изменении ConfigMap

**Решение:** Добавьте аннотацию в Deployment, чтобы pod перезапускался:
```yaml
template:
  metadata:
    annotations:
      checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
```

Или используйте:
```bash
kubectl rollout restart deployment/backend -n default
```

### Проблема: Frontend не может подключиться к backend

**Проверьте:**
1. Service backend существует: `kubectl get svc backend -n default`
2. DNS работает внутри pod:
   ```bash
   kubectl exec -it <frontend-pod> -- nslookup backend
   ```
3. CORS настроен в backend (уже есть в нашем app.py)

---

## Дополнительные эксперименты

### 1. Добавить новый микросервис

Создайте `k8s/microservices/database/` с манифестами для PostgreSQL или Redis.

### 2. Использовать Secrets

Замените некоторые данные в ConfigMap на Secrets:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: backend-secret
type: Opaque
data:
  API_KEY: base64-encoded-value
```

### 3. Multi-environment с Kustomize

Создайте структуру:
```
k8s/
  base/           # Базовые манифесты
  overlays/
    dev/          # Dev окружение
    prod/         # Prod окружение
```

### 4. Добавить проверки перед синхронизацией

Pre-sync hooks, post-sync hooks для запуска миграций БД и т.д.

---

## Проверочный список GitOps принципов

После прохождения всех сценариев, вы должны убедиться в:

- ✅ **Декларативность**: Весь desired state в git
- ✅ **Версионирование**: Все изменения через git commits
- ✅ **Автоматизация**: ArgoCD автоматически применяет изменения
- ✅ **Иммутабельность**: Изменения только через git, не вручную
- ✅ **Self-healing**: Ручные изменения откатываются автоматически
- ✅ **Observability**: Видно состояние, историю, события

---

## Очистка

Чтобы удалить все ресурсы:

```bash
# Удалить приложение из ArgoCD
~/.local/bin/argocd app delete microservices-app

# Или через kubectl
kubectl delete -f argocd-microservices-app.yaml

# Удалить все pods
kubectl delete all --all -n default
```

---

## Полезные ссылки

- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [GitOps Principles](https://opengitops.dev/)
- [Sync Waves](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-waves/)
- [ArgoCD Best Practices](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/)
