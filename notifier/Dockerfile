# docker build -t notifier:latest .
# docker run --network host notifier:latest

FROM python:3.10-slim-bullseye

COPY ./src /src

WORKDIR /src

RUN python -m pip install -r requirements.txt

CMD [ "python", "notifier.py" ]
