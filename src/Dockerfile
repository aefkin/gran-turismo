FROM python:3.7

WORKDIR /app/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y time && rm -rf /var/apt/cache/*

COPY requirements.pip /app/

RUN pip install -r /app/requirements.pip

COPY gran_turismo/ /app/gran_turismo/

COPY run.sh /app/run.sh

RUN chmod +x /app/run.sh

WORKDIR /app/gran_turismo/