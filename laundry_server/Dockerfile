# docker build -t laundry_server:latest .
# docker run -p 5000:5000 laundry_server:latest

FROM python:3.10-slim-bullseye

COPY ./src /src

WORKDIR /src

RUN python -m pip install -r static/requirements.txt

CMD [ "python", "app.py" ]
