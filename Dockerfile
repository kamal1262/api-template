FROM python:3.7-alpine

COPY requirements.txt /

RUN pip install -r requirements.txt

RUN apk update && \
    apk upgrade && \
    apk add curl vim

WORKDIR /app

COPY . /app

RUN pip install gunicorn

EXPOSE 8000

ENTRYPOINT ["sh", "/app/entrypoint.sh"]