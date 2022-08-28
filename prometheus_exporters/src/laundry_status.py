from time import sleep, time

import requests
from prometheus_client import start_http_server, Gauge


AVAILABLE_STATUSES = {'Available', 'End of cycle'}

availability = Gauge('laundry_availability',
                     'Machine availability at each hall',
                     ['village', 'hall', 'type'])

availability.labels('Poly Canyon Village', 'Estrella', 'Washer').set(3)

maintenance = Gauge('maintence', 'Maintenance metrics', ['job'])


def update_metrics():
    halls_req = requests.get('http://localhost:5000/get_halls')
    assert halls_req.status_code == 200
    halls = halls_req.json()

    for hall in halls.values():
        hall_name = hall['hallName']
        hall_id = hall['hallId']
        village = hall['village']

        prom_labels = [village, hall_name]

        hall_req = requests.get(f'http://localhost:5000/hall_status/{hall_id}')
        assert hall_req.status_code == 200, hall_id

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


start_http_server(10000)
while True:
    start = time()
    update_metrics()
    end = time()

    print('Collected metrics in %.1f seconds' % (end - start))

    maintenance.labels('availability').set(end - start)

    sleep(60)
