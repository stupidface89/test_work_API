FROM python:3.11

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV DJANGO_SETTINGS_MODULE 'todo.settings'

WORKDIR /opt/app

COPY ./app/requirements.txt .

RUN pip install --upgrade pip \
    pip install -r requirements.txt

