from http import HTTPStatus

import laundry_util


def get_hall_status(hall_id: str):
    html = laundry_util.get_hall_html(hall_id)
    machines = laundry_util.get_hall_machines(html)

    return machines, HTTPStatus.OK
