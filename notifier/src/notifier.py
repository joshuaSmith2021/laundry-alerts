# Script to queue availability alerts for fulfillment in redis database.
# Copyright (C) 2022 Joshua Smith

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
from time import sleep

import redis


def manage_alert(alert: dict, conn: redis.Redis):
    alert_key = alert['key']

    subscribers = conn.hget('subscriptions', alert_key)

    if subscribers is None:
        return

    # Delete subscription, as it has already been handled
    conn.hdel('subscriptions', alert_key)

    subscribers = json.loads(subscribers)

    while subscribers:
        current = subscribers.pop()
        fulfillment_method = current['fulfillment']

        notification = {
            'target': current['user'],
            'message': alert['message']
        }

        if fulfillment_method == 'discord':
            conn.rpush('discord_alerts', json.dumps(notification))


def queue_loop(conn: redis.Redis):
    while True:
        while alert_str := conn.lpop('alerts'):
            alert = json.loads(alert_str)
            manage_alert(alert, conn)

        sleep(5)


if __name__ == '__main__':
    conn = redis.Redis(host='laundry_redis', port=6379, db=0)
    queue_loop(conn)
