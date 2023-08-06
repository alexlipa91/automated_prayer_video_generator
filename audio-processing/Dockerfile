FROM xserrat/facebook-demucs

COPY src /src
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY audio-processing/run.sh /run.sh

ENTRYPOINT ["/bin/bash", "/run.sh"]

