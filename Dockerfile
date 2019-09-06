FROM python:3.7-alpine

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

RUN pip install gunicorn

EXPOSE 8000

ENTRYPOINT ["sh", "/app/entrypoint.sh"]