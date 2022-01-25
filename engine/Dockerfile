FROM python:alpine

ENV APP_HOME /engine
WORKDIR ${APP_HOME}

COPY paketi.txt .
COPY app.py .
COPY ./model/ ./model/

RUN apk add gcc musl-dev libffi-dev && pip install -r paketi.txt

CMD ["python", "app.py"]