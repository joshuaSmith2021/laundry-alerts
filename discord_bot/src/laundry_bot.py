import os

import discord
from discord.ext import commands

from laundry_cog import Laundry


DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
assert DISCORD_TOKEN is not None

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    await bot.add_cog(Laundry(bot))

    activity = discord.Activity(name='!help', type=discord.ActivityType.listening)
    await bot.change_presence(activity=activity)


bot.run(DISCORD_TOKEN)
