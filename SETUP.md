# Инструкция по настройке проекта

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Настройка переменных окружения

Создайте файл `.env` в корне проекта на основе следующего шаблона:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@mailingservice.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password

# Cache Settings
CACHE_BACKEND=django.core.cache.backends.locmem.LocMemCache
CACHE_LOCATION=default
```

## Миграции базы данных

Выполните миграции для создания структуры базы данных:

```bash
python manage.py makemigrations
python manage.py migrate
```

**Примечание:** Если при выполнении миграций возникает ошибка `InconsistentMigrationHistory`, это означает, что миграции были применены в неправильном порядке. В этом случае:

1. Остановите сервер Django (если он запущен)
2. Удалите файл `db.sqlite3` (если это не критично для ваших данных)
3. Выполните миграции заново:

```bash
python manage.py migrate
```

Или используйте скрипт для исправления порядка миграций (см. `fix_migrations.py` в корне проекта, если он существует).

## Создание группы менеджеров

Для создания группы "Менеджеры" с соответствующими правами выполните:

```bash
python manage.py create_managers_group
```

## Создание суперпользователя

```bash
python manage.py createsuperuser
```

## Запуск сервера разработки

```bash
python manage.py runserver
```

## Использование команды отправки рассылок

Для автоматической отправки рассылок по расписанию используйте:

```bash
python manage.py send_mailings
```

Рекомендуется настроить cron или планировщик задач для автоматического запуска этой команды.


