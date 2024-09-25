FROM python:3.10-slim
FROM continuumio/miniconda3:latest

WORKDIR /app

ADD . /app

RUN apt-get update &&\
  apt-get install -y\
  bash \
  build-essential\
  gcc\
  libffi-dev\
  musl-dev\
  openssl\
  libpq-dev

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]