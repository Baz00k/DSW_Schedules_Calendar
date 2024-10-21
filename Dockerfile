FROM python:3-alpine

COPY . ./dswsc

WORKDIR /dswsc

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
