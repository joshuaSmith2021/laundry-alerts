import re
from typing import List, Tuple

import requests


def get_hall_html(hall_id: str) -> str:
    """
    Gets HTML document from washalert
    """

    # Get html page
    base_url = 'http://washalert.washlaundry.com' + \
               '/washalertweb/calpoly/WASHALERtweb.aspx'

    req = requests.get(base_url, params={'location': hall_id})
    assert req.status_code == 200, f'HTTP request received {req.status_code}'

    return req.text


def get_hall_machines(html: str) -> List[Tuple[str]]:
    """
    Finds machines from html document and returns a list of regex matches.
    Each match is a tuple of strings:
        [0]: name
        [1]: type (Washer|Dryer)
        [2]: availability
        [3]: time
    """

    # Clean up html
    html = re.sub(r'<img.*?>', '', html)  # Remove img tags from html

    # Get machines from text
    machine_pattern = re.compile(r'<tr class="Machine(?:.|\n)+?name">(.+?)<(?:.|\n)+?type">(.+?)<(?:.|\n)+?status">(.+?)<(?:.|\n)+?time">(.+?)<(?:.|\n)+?<\/tr>')
    machine_matches = machine_pattern.findall(html)

    machines = []
    for match in machine_matches:
        machines.append({
            'name': match[0],
            'type': match[1],
            'availability': match[2],
            'time': match[3]
        })

    return machines


if __name__ == '__main__':
    foxen_id = '6a7d18d3-6225-417d-874f-ddc72b878219'
    html = get_hall_html(foxen_id)
    print(get_hall_machines(html))
