import json
from difflib import SequenceMatcher

import requests
from redis import Redis
from discord.ext import commands


class Laundry(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = Redis(host='localhost', port=6379, db=0)

        # Fetch hall names
        retries = 0
        self.HALL_DATA = None
        while retries < 10:
            req = requests.get('http://localhost:5000/get_halls')

            if req.status_code != 200:
                retries += 1
                continue

            self.HALL_DATA = req.json()
            break

        assert self.HALL_DATA is not None, 'FATAL: Failed to fetch hall names'

    def detect_hall(self, *words):
        '''
        Loops through each word in words, and if one is detected to be present
        in self.HALL_NAMES, return that word as it appears in self.HALL_NAMES.
        '''

        if not words:
            return (0, '')

        for word in words:
            top_result = (0, '')
            for hall in self.HALL_DATA:
                # s is the similarity score
                s = SequenceMatcher(None, word.lower(), hall.lower()).ratio()
                if s > top_result[0]:
                    top_result = (s, hall)

            return top_result

    def register_user(self, machine_type, ctx, *args):
        '''
        Add user's notification to subscriptions hashmap
        '''

        # First, figure out if the user specified a residence hall
        certainty, detected_hall = self.detect_hall(*args)

        if certainty > 0.85:
            # Count this detection as a match
            self.conn.hset('discord_residence', ctx.author.id, detected_hall)

        res_hall_redis = self.conn.hget('discord_residence', ctx.author.id)

        if res_hall_redis is None:
            return 'Residence hall not found, please specify a building.' + \
                   ' ex: `!washer aliso`'

        residence_hall = res_hall_redis.decode('utf-8')

        # Get residence hall data
        print(residence_hall)
        hall_data = self.HALL_DATA[residence_hall]

        # Build key
        subscription_key = '.'.join([hall_data['village'], residence_hall,
                                     machine_type])

        # Build subscription object
        subscription = {
            'fulfillment': 'discord',
            'user': ctx.author.id
        }

        # Get current state of db
        current_state = self.conn.hget('subscriptions', subscription_key)
        subscriptions = json.loads(current_state if current_state else '[]')

        # Update db
        subscriptions.append(subscription)
        new_state = json.dumps(subscriptions)
        self.conn.hset('subscriptions', subscription_key, new_state)

        return 'You will be notified when a %s is available in %s.' % \
               (machine_type, residence_hall)

    @commands.command()
    async def forget(self, ctx):
        '''
        Delete your residence hall information from the database.
        '''

        deleted = self.conn.hdel('discord_residence', ctx.author.id)
        if deleted:
            await ctx.channel.send('Your residence hall was deleted.')
        else:
            await ctx.channel.send('Your residence was already not saved.')

    @commands.command()
    async def washer(self, ctx, *context):
        '''
        Subscribe to alerts for washers in your residence hall. If this is
        your first time using this command, you will need to specify the
        residence hall for which you would like to receive notifications.

        You will only receive one alert per command. Once the alert is sent,
        you will have to reuse this command to receive another alert when a
        washer becomes available.
        '''

        registration = self.register_user('Washer', ctx, *context)
        await ctx.channel.send(registration)

    @commands.command()
    async def dryer(self, ctx, *context):
        '''
        Subscribe to alerts for dryers in your residence hall. If this is
        your first time using this command, you will need to specify the
        residence hall for which you would like to receive notifications.

        You will only receive one alert per command. Once the alert is sent,
        you will have to reuse this command to receive another alert when a
        dryer becomes available.
        '''

        registration = self.register_user('Dryer', ctx, *context)
        await ctx.channel.send(registration)
