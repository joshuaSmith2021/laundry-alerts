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
