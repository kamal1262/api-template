FROM python:3.7-slim-buster

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

RUN apt-get update && \
    apt-get install -y curl vim

RUN pip install gunicorn

EXPOSE 8000

ENTRYPOINT ["sh", "/app/entrypoint.sh"]
