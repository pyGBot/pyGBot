FROM docker.io/python:2.7.18

WORKDIR /app/

RUN pip install twisted==20.3.0 \
    && pip install pyOpenSSL==21.0.0

COPY contrib contrib/
COPY pyGBot pyGBot/
COPY hashpw.py runpyGBot.py ./

ENTRYPOINT [ "python", "runpyGBot.py" ]
