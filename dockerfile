FROM python:3.8.2-slim-buster

USER root

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get update && pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python","PY0013_UK_Postcodes.py"]
