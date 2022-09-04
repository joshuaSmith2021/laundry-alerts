# laundry-alerts
A collection of servers and services that work together to send Cal Poly
students living on campus alerts when laundry machines become available on
campus.

### tech stack
- laundry_server is a connexion flask app using openapi specification. This server fetches data from the washalert website and uses regex to scrape the machine data from the webpage. This server runs in a docker container.
- prometheus\_exporters is a [prometheus exporter](https://prometheus.io/docs/instrumenting/exporters/) written in Python. It calls the laundry\_server for data. This script runs in a docker container.
- watcher and notifier are Python scripts that take data from the prometheus exporter and update the [Redis](https://redis.com/) database. When machines are detected to be available, the watcher (this script *watches* the machine states) sends an alert to the Redis database. The notifier then checks to see which users, if any, have subscribed to this event, and then sends an alert to a fulfillment queue.
- discord\_bot is a discord bot written using [discord.py](https://discordpy.readthedocs.io/en/stable/). This bot listens to user commands, does basic word processing, and then adds a subscription to the Redis database. It also dequeues notifications from the discord_alerts queue in Redis and sends the notifications to their target recipients.
