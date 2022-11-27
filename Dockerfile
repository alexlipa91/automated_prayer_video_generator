FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y ffmpeg imagemagick

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY src /src
COPY resources /resources

COPY credentials.json /credentials.json
ENV GOOGLE_APPLICATION_CREDENTIALS=/credentials.json
COPY credentials.storage /credentials.storage
ENV CREDENTIALS_FILE=/credentials.storage

RUN mv /etc/ImageMagick-6/policy.xml /etc/ImageMagick-6/policy.xml.bkp
RUN grep -v pattern="@*" /etc/ImageMagick-6/policy.xml.bkp > /etc/ImageMagick-6/policy.xml

ENTRYPOINT ["python3", "/src/main.py"]