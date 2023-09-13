# Дипломный проект "Фудграм"

***
### Описание проекта
«Фудграм» — сайт, на котором пользователи публикуют рецепты, добавляют чужие рецепты в избранное и подписываются на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
***


## Tech

- Python 3.x.x
- React for frontend
- Django for backend
- Nginx
- Docker
- Postgres


## Деплой

- Клонирование репозитория (на удалённом сервере понадобится только 'infra/'):

```
git@github.com:theslayah/foodgram-project-react.git
```

- Подключение к серверу:

```
ssh -i <путь к ключу> <server user>@<server ip>
```

- Создать директорию проекта:

```
mkdir foodgram && cd foodgram/
```

- Создать файл .env:

```
touch .env
```

- В env файле прописать:

```
SECRET_KEY=<secret key>
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<password>
DB_HOST=db
DB_PORT=5432
ALLOWED_HOSTS=<hosts>
```

- Скопировать содержимое папки infra/ с локальной машины на удалённый сервер:

```
scp -r -i <путь к ключу> <путь к папке> <server user>@<server ip>:/home/<server user>/foodgram/
```

- Запустить docker-compose.production.yml:

```
sudo docker compose -f docker-compose.production.yml up -d
```

- Выполнить миграции, собрать статику, создать суперпользователя:

```
sudo docker compose exec backend python manage.py makemigrations
sudo docker compose exec backend python manage.py migrate
sudo docker compose exec backend python manage.py collectstatic
sudo docker compose exec backend cp -r /app/collected_static/. /app/backend_static/static/
sudo docker compose exec backend python manage.py createsuperuser
```

## Ссылки
### Админка:
http://feedgram.onthewifi.com:7000/admin
### Проект:
http://feedgram.onthewifi.com:7000/

## Авторы:
- Frontend: YandexMaster
- Backend & Devploy: theslayah 
