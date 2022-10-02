# Write functions to aid in scraping machine data from the web.
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

import re
from typing import List, Tuple

import requests


def get_villages() -> List[Tuple[str]]:
    """
    Gets the url and name of each residential village in Cal Poly. Examples of
    residential villages: Cerro Vista, North Mountain, etc.
    """

    directory = 'http://washalert.washlaundry.com' + \
                '/washalertweb/calpoly'

    url = f'{directory}/cal-poly.html'

    req = requests.get(url)
    assert req.status_code == 200, f'HTTP request received {req.status_code}'

    html = req.text

    # Extract table html from html
    table_pattern = re.compile(r'(?:<table>)((.|\n)+?)(?:<\/table>)')
    table_html = next(filter(lambda x: x.strip(), table_pattern.findall(html)[0]))

    entry_pattern = re.compile(r'<td><a href="(.+?)">(.+?)<\/a><\/td>')
    table_entries = entry_pattern.findall(table_html)

    result = []
    for href, village in table_entries:
        village_url = f'{directory}/{href}'
        village_name = re.sub(r'\s+', ' ', village)
        result.append((village_url, village_name))

    return result


def get_village_halls(url: str) -> List[Tuple[str]]:
    """
    Get the halls in a village from the url.
    """

    req = requests.get(url)
    assert req.status_code == 200, f'HTTP request received {req.status_code}'
    html = req.text

    hall_pattern = re.compile(r'<td><a href=".+?location=(.*?)"(?:.*?)>(.+?)<\/a><\/td>')
    hall_matches = hall_pattern.findall(html)

    return hall_matches


def get_hall_html(hall_id: str) -> str:
    """
    Gets HTML document from washalert for the hall with the given id
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
    machine_pattern = re.compile(r'<tr class="Machine(?:.|\n)+?name">(.+?)<(?:.|\n)+?type">(.+?)<(?:.|\n)+?status">(.+?)<(?:.|\n)+?time">(?:<div.+?<div.+?<\/div><\/div>)?(.+?)<(?:.|\n)+?<\/tr>')
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
    hall_id = '676b5302-485a-4edb-8b36-a20d82a3ae20'
    html = get_hall_html(hall_id)
    print(get_hall_machines(html))

    # villages = get_villages()
    # print(get_village_halls(villages[2][0]))

    halls = [get_village_halls(x[0]) for x in villages]
