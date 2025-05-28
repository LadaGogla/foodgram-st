# Foodgram

Foodgram - это веб-приложение для публикации рецептов. Пользователи могут создавать рецепты, подписываться на других авторов, добавлять рецепты в избранное и формировать список покупок.

## Технологии

- Python 3.9
- Django 3.2
- Django REST Framework
- PostgreSQL
- Docker
- Nginx

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone <url-репозитория>
cd foodgram
```

2. Создайте файл `.env` в папке `backend` со следующими переменными:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=your-secret-key
DEBUG=False
```

3. Запустите проект с помощью Docker Compose:
```bash
cd infra
docker-compose up -d
```

4. Выполните миграции:
```bash
docker-compose exec backend python manage.py migrate
```

5. Создайте суперпользователя:
```bash
docker-compose exec backend python manage.py createsuperuser
```

6. Загрузите ингредиенты:
```bash
docker-compose exec backend python manage.py load_ingredients
```

7. Соберите статические файлы:
```bash
docker-compose exec backend python manage.py collectstatic --no-input
```

После этого проект будет доступен по адресу http://localhost/

## API Endpoints

- `/api/users/` - управление пользователями
- `/api/tags/` - теги рецептов
- `/api/ingredients/` - ингредиенты
- `/api/recipes/` - рецепты
- `/api/users/{id}/subscribe/` - подписка на пользователя
- `/api/recipes/{id}/favorite/` - добавление в избранное
- `/api/recipes/{id}/shopping_cart/` - добавление в список покупок
- `/api/recipes/download_shopping_cart/` - скачать список покупок

## Автор

[Ваше имя]

