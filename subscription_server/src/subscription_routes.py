# Not in production. See ./app.py for information.
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
from http import HTTPStatus

import redis


conn = redis.Redis(host='localhost', port=6379, db=0)


def subscribe(event_key: str, fulfillment: str, user: str):
    # If the machine or hall is already available, store a message stating so.
    already_available = None

    # Update message will be sent to the client. The format of this message
    # varies based on whether a residence hall or specific machine is being
    # requested.
    update_message = None

    if event_key.count('.') == 3:
        # Specific machine
        current_state = conn.hget('machine_availability', event_key)
        if current_state is not None and int(current_state) == 0:
            already_available = 'That machine is already available.'

        update_message = 'You will be notified when the machine is ready.'

    elif event_key.count('.') == 2:
        # Residence hall
        current_state = conn.hget('hall_availability', event_key)
        if current_state is not None and int(current_state):
            already_available = 'There is already a machine available.'

        update_message = 'You will be notified when a machine is available.'

    else:
        return 'Invalid event_key', HTTPStatus.BAD_REQUEST

    if already_available is not None:
        # The machine is already available. Return a 202 response along with a
        # message stating that the requested resourse is available.
        return already_available, HTTPStatus.ACCEPTED

    # Get the current subscriptions for the given event_key
    current_state = conn.hget('subscriptions', event_key)
    subscriptions = json.loads(current_state if current_state else '[]')

    new_subscription = {
        'fulfillment': fulfillment,
        'user': user
    }

    subscriptions.append(new_subscription)

    # Update redis with new subscription
    conn.hset('subscriptions', event_key, json.dumps(subscriptions))

    # Return a 201 CREATED with message to send to client
    return update_message, HTTPStatus.CREATED
