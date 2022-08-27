import re
from http import HTTPStatus

import laundry_util


def get_hall_status(hall_id: str):
    html = laundry_util.get_hall_html(hall_id)
    machines = laundry_util.get_hall_machines(html)

    return machines, HTTPStatus.OK


def get_halls():
    villages = laundry_util.get_villages()

    # Convert some special html codes to more common characters
    char_convert_dict = {
        '&#696;': '',
        '&scaron;': 's',
        '&#660;': '',
        '&#322;': 'l',
        '&#616;': 'i'
    }

    char_convert = lambda x: char_convert_dict[x.group()]

    char_convert_pattern_string = f'({"|".join(char_convert_dict.keys())})'
    char_convert_pattern = re.compile(char_convert_pattern_string)

    result = {}
    for village_url, village_name in villages:
        halls = laundry_util.get_village_halls(village_url)
        village_name = char_convert_pattern.sub(char_convert, village_name)

        for hall_id, hall_name in halls:
            if village_name == 'yakitutu':
                hall_name = re.sub(r'Bldg \w - ', '', hall_name).strip()

            hall_name = char_convert_pattern.sub(char_convert, hall_name)

            result[hall_name] = {
                'village': village_name,
                'hallId': hall_id,
                'hallName': hall_name
            }

    return result, HTTPStatus.OK
