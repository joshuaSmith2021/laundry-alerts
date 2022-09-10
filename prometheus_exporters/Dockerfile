# docker build -t exporters/laundry_status:latest .
# docker run --network host -d exporters/laundry_status:latest

FROM python:3.10-slim-bullseye

COPY ./src /src

WORKDIR /src

RUN python -m pip install -r requirements.txt

CMD [ "python", "laundry_status.py" ]
