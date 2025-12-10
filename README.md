# Hello World!

## RUN

Create database file before anything, or just make sure it exists in `src` folder 
```bash
touch src/db.sqlite3
```

Build Docker image
```bash
docker compose build
```

PLEASE USE DOCKER COMPOSE
```bash
docker compose up -d
```

## Run locally

Make sure you have all migrations done.

!!! All commands should be run in `src` directory !!!
```bash
python manage.py makemigrations
```

```bash
python manage.py runserver 127.0.0.1:8000
```

## (Optional) Create super your admin account
Please log in into the admin panel only in incognito mode:
http://127.0.0.1:8000/admin
```bash
python manage.py createsuperuser
```
