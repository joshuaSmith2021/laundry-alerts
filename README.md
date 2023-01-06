# laundry-alerts
A collection of servers and services that work together to send Cal Poly
students living on campus alerts when laundry machines become available on
campus.

# Note
Unfortunately, Cal Poly launched a mobile application that manages machine info,
and the website from which I formerly scraped data has been taken down. Unfortunately,
this means that [the laundry data server](https://github.com/joshuaSmith2021/laundry-alerts/tree/master/laundry_server)
is broken. Fortunately, writing a new web scraper would fix the entire project, which
is up next on the todo list for this project.

# Usage
`docker compose up` should make you right as rain to run everything except for
the discord bot. To run the discord bot, make a .env file in discord_bot/
containing a discord bot token, defined in .env as DISCORD_TOKEN.

### tech stack
- laundry_server is a connexion flask app using openapi specification. This server fetches data from the washalert website and uses regex to scrape the machine data from the webpage. This server runs in a docker container.
- prometheus\_exporters is a [prometheus exporter](https://prometheus.io/docs/instrumenting/exporters/) written in Python. It calls the laundry\_server for data. This script runs in a docker container.
- watcher and notifier are Python scripts that take data from the prometheus exporter and update the [Redis](https://redis.com/) database. When machines are detected to be available, the watcher (this script *watches* the machine states) sends an alert to the Redis database. The notifier then checks to see which users, if any, have subscribed to this event, and then sends an alert to a fulfillment queue.
- discord\_bot is a discord bot written using [discord.py](https://discordpy.readthedocs.io/en/stable/). This bot listens to user commands, does basic word processing, and then adds a subscription to the Redis database. It also dequeues notifications from the discord_alerts queue in Redis and sends the notifications to their target recipients.
