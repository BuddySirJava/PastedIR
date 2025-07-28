# Use official Python image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/

# Set Django settings module explicitly
ENV DJANGO_SETTINGS_MODULE=pastebinir.settings

# Debug: List directory contents before collectstatic
RUN ls -l /app && ls -l /app/pastebinir

# Collect static files
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "pastebinir.wsgi:application", "--bind", "0.0.0.0:8000"] 