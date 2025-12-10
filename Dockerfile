FROM python:3.10-slim AS builder

# System deps for psycopg2, Pillow, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    libpq-dev \
    libjpeg62-turbo-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Copy project
COPY ./src /app

# Startup procedure DB migrations
RUN python manage.py makemigrations
RUN python manage.py migrate

# Default command is dev server (overridden in prod compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

EXPOSE 8000
