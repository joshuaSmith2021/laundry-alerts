# docker build -t subscription_server:latest .
# docker run --network host subscription_server:latest

FROM python:3.10-slim-bullseye

COPY ./src /src

WORKDIR /src

RUN python -m pip install -r static/requirements.txt

CMD [ "python", "app.py" ]
