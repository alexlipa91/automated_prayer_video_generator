FROM python:3.11-slim-buster

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    imagemagick \
    build-essential \
    ffmpeg \
    git \
    python3 \
    python3-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt

COPY video_generator video_generator
COPY resources /resources

# COPY credentials.json /credentials.json

RUN mv /etc/ImageMagick-6/policy.xml /etc/ImageMagick-6/policy.xml.bkp
RUN grep -v pattern="@*" /etc/ImageMagick-6/policy.xml.bkp > /etc/ImageMagick-6/policy.xml

ENTRYPOINT ["python3", "-u", "video_generator/src/main.py"]