import json
import re
import time

import redis
import requests


def parse_labels(labels: str) -> dict:
    labels = labels.strip('{}').replace('"', '')
    pairs = labels.split(',')

    result = {}
    for pair in pairs:
        key, value = pair.split('=')
        result[key] = value

    return result


def update_statuses(conn: redis.Redis):
    exporter_req = requests.get('http://localhost:10000')
    if exporter_req.status_code != 200:
        print('Failed to get a 200 status from exporter')
        return

    hall_availability = re.compile(r'laundry_availability({.+?}) (\d+)')
    halls_matches = hall_availability.findall(exporter_req.text)

    for match in halls_matches:
        labels, value = match
        value = int(value)
        hall_data = parse_labels(labels)

        village = hall_data['village']
        hall_name = hall_data['hall']
        machine_type = hall_data['type']

        machines_key = '.'.join([village, hall_name, machine_type])

        previous_state = conn.hget('hall_availability', machines_key)

        # If this hall previously had none available and now does, queue an
        # alert
        if previous_state == 0 and value:
            plural = '' if value == 1 else 's'
            notification = {
                'message': f'There is now {value} {machine_type}{plural} in {hall_name}',
                'type': 'hall_availability',
                'key': machines_key
            }

            print(f'Pushing {notification} to alerts')
            conn.rpush('alerts', json.dumps(notification))

        conn.hset('hall_availability', machines_key, value)

    machine_time = re.compile(r'machine_time{(.+?)} (\d+)')
    machine_matches = machine_time.findall(exporter_req.text)

    for machine in machine_matches:
        label_string, time_remaining = machine
        machine_labels = parse_labels(label_string)
        time_remaining = int(time_remaining)

        machine_key_names = ('village', 'hall', 'type', 'name')
        machine_key = '.'.join(map(lambda x: machine_labels[x],
                                   machine_key_names))

        previous_state = conn.hget('machine_availability', machine_key)
        if previous_state is not None:
            previous_state = int(previous_state)

        if previous_state and time_remaining == 0:
            # Machine just finished
            type_ = machine_labels['type']
            name = machine_labels['name']
            notification = {
                'message': f'{type_} {name} just finished',
                'type': 'machine_availability',
                'key': machine_key
            }

            print(f'Pushing {notification} to alerts')
            conn.rpush('alerts', json.dumps(notification))

        conn.hset('machine_availability', machine_key, time_remaining)


if __name__ == '__main__':
    conn = redis.Redis(host='localhost', port=6379, db=0)
    while True:
        update_statuses(conn)
        time.sleep(5)
