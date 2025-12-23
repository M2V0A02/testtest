# Инструкции по работе с Argo CD

## Статус установки

✅ Argo CD установлен в namespace `argocd`
✅ Port-forward запущен на порту 8080
✅ Локальный git репозиторий инициализирован
✅ Тестовое приложение создано

## Доступ к Argo CD UI

**URL:** https://localhost:8080 (или http://localhost:8080)

**Credentials:**
- Username: `admin`
- Password: `2jCE1952fifemCft`

> **Примечание:** При открытии в браузере вы можете увидеть предупреждение о сертификате - это нормально для локальной установки. Просто продолжите (Advanced -> Proceed).

## Использование Argo CD CLI

Argo CD CLI установлен в: `~/.local/bin/argocd`

Для использования добавьте в PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

Или используйте полный путь:
```bash
~/.local/bin/argocd version
```

Войти в Argo CD:
```bash
~/.local/bin/argocd login localhost:8080 --insecure --username admin --password 2jCE1952fifemCft
```

## Созданные файлы

1. **argocd-app.yaml** - Application для демо-приложения guestbook
2. **argocd-app-local.yaml** - Шаблон для вашего локального приложения
3. **k8s/test-app/** - Kubernetes манифесты для nginx приложения

## Как использовать ваш локальный репозиторий

### Вариант 1: Запушить на GitHub/GitLab

```bash
# Создайте репозиторий на GitHub/GitLab
# Затем выполните:
git remote add origin https://github.com/your-username/argo-cd-test.git
git push -u origin master

# Отредактируйте argocd-app-local.yaml, заменив REPLACE_WITH_YOUR_REPO_URL
# на URL вашего репозитория, затем:
kubectl apply -f argocd-app-local.yaml
```

### Вариант 2: Использовать текущее демо-приложение

Уже развернуто приложение `test-nginx-app` из публичного репозитория.

Проверить статус:
```bash
kubectl get applications -n argocd
kubectl get pods -n default
```

## Полезные команды

### Просмотр приложений
```bash
kubectl get applications -n argocd
~/.local/bin/argocd app list
```

### Просмотр деталей приложения
```bash
~/.local/bin/argocd app get test-nginx-app
```

### Синхронизация приложения вручную
```bash
~/.local/bin/argocd app sync test-nginx-app
```

### Просмотр логов Argo CD
```bash
kubectl logs -n argocd deployment/argocd-server
kubectl logs -n argocd deployment/argocd-repo-server
```

### Просмотр всех pods Argo CD
```bash
kubectl get pods -n argocd
```

## Устранение неполадок

### Repo-server в CrashLoopBackOff

Если `argocd-repo-server` не запускается, попробуйте:
```bash
kubectl delete pod -n argocd -l app.kubernetes.io/name=argocd-repo-server
```

### Проверка статуса port-forward

Port-forward должен работать на порту 8080. Проверить:
```bash
netstat -tlnp | grep 8080
# или
ss -tlnp | grep 8080
```

Если не работает, перезапустите:
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443 --address='0.0.0.0' &
```

## Удаление тестового окружения

Для удаления всего окружения:
```bash
# Удалить приложение
kubectl delete -f argocd-app.yaml

# Удалить Argo CD
kubectl delete -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl delete namespace argocd
```
