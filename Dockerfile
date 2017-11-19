#https://hub.docker.com/_/python/
FROM python:2

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY unisanews/instance ./instance
COPY unisanews/templates ./templates

COPY unisanews/unisanews.py .
COPY unisanews/crawler.py .
COPY unisanews/storage.py .
COPY unisanews/entities.py .

EXPOSE 5000

CMD [ "python", "./unisanews.py" ]
