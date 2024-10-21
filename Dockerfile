FROM python:3-alpine

WORKDIR /app

COPY . ./dswsc

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
