#https://hub.docker.com/_/python/
FROM python:2

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY instance ./instance
COPY unisanews/templates ./templates
COPY unisanews/static ./static
COPY unisanews/schema.sql ./

COPY unisanews/*.py ./

CMD ["python", "./unisanews.py"]
