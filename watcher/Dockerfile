# docker build -t laundry_watcher:latest .
# docker run -d --network host laundry_watcher:latest

FROM python:3.10-slim-bullseye

COPY ./src /src

WORKDIR /src

RUN python -m pip install -r requirements.txt

CMD [ "python", "watcher.py" ]
