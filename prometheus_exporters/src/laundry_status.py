from time import sleep, time

import requests
from prometheus_client import start_http_server, Gauge


AVAILABLE_STATUSES = {'Available', 'End of cycle'}

availability = Gauge('laundry_availability',
                     'Machine availability at each hall',
                     ['village', 'hall', 'type'])

availability.labels('Poly Canyon Village', 'Estrella', 'Washer').set(3)

maintenance = Gauge('maintenance', 'Maintenance metrics', ['job'])

failures = Gauge('failures', 'Hall failures', ['village', 'hall'])


def update_metrics(retries):
    halls_req = requests.get('http://localhost:5000/get_halls')

    if halls_req.status_code != 200 and retries < 10:
        # Something is wrong with get_halls, start the function again
        print(f'halls_req failed to get a 200 response (retries={retries})')
        print(halls_req.text)
        update_metrics(retries + 1)
        return
    elif halls_req.status_code != 200:
        # The function has failed 10 times
        print('halls_req has failed to get a 200 response 10 times. Exiting.')
        exit(1)

    halls = halls_req.json()

    for hall in halls.values():
        hall_name = hall['hallName']
        hall_id = hall['hallId']
        village = hall['village']

        prom_labels = [village, hall_name]

        hall_req = requests.get(f'http://localhost:5000/hall_status/{hall_id}')
        if hall_req.status_code != 200:
            # This one hall failed. Hopefully this stops
            failures.labels(*prom_labels).set(1)
            continue

        hall_data = {
            'Washer': 0,
            'Dryer': 0
        }

        machines = hall_req.json()

        for machine in machines:
            if machine['availability'] in AVAILABLE_STATUSES:
                hall_data[machine['type']] += 1

        for key, value in hall_data.items():
            availability.labels(*prom_labels, key).set(value)
            failures.labels(*prom_labels).set(0)


start_http_server(10000)
while True:
    start = time()
    update_metrics(0)
    end = time()

    print('Collected metrics in %.1f seconds' % (end - start))

    maintenance.labels('availability').set(end - start)

    sleep(60)
