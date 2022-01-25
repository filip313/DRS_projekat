FROM python:alpine

ENV APP_HOME /web
WORKDIR $APP_HOME

COPY paketi.txt .
COPY app.py .
COPY ./user/ ./user/
COPY ./transakcije ./transakcije

RUN apk add libffi-dev && pip install -r paketi.txt

CMD ["python", "app.py"]