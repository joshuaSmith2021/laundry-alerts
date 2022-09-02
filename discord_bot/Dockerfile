# docker build -t laundry_bot:latest .
# docker run --network host --env-file .env laundry_bot:latest

# env file should have DISCORD_TOKEN set to a value

FROM python:3.10-slim-bullseye

COPY ./src /src

WORKDIR /src

RUN python -m pip install -r requirements.txt

CMD [ "python", "laundry_bot.py" ]
