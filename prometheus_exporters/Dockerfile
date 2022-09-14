# docker build -t exporters/laundry_status:latest .
# docker run --network host -d exporters/laundry_status:latest

FROM python:3.10-slim-bullseye

# Install curl, which is not available by default on python images
RUN apt-get update && \
    apt-get install -y curl

COPY ./src /src

WORKDIR /src

RUN python -m pip install -r requirements.txt

CMD [ "python", "laundry_status.py" ]
