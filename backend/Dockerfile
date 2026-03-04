FROM python:3.12-alpine
ADD requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

ADD . /app/backend

WORKDIR /app

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]