FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y ffmpeg imagemagick

COPY src /src
COPY requirements.txt requirements.txt

COPY credentials.json /credentials.json
ENV GOOGLE_APPLICATION_CREDENTIALS=/credentials.json

RUN pip3 install -r requirements.txt

RUN ls /src

ENTRYPOINT ["python3", "/src/main.py"]