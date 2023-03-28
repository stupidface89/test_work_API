FROM python:3.11-bullseye

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV DJANGO_SETTINGS_MODULE 'todo.settings'

EXPOSE 8000/tcp

WORKDIR /opt/app

COPY ./app/requirements.txt .

RUN pip install --upgrade pip \
    pip install -r requirements.txt

COPY ./app/ .

COPY app/entrypoint.sh .

CMD ["./entrypoint.sh"]