"""
dThis file is the main entry point of the bot
"""

from multiprocessing.util import debug
import logging
from src.bot_state import BotState
import discord
import os

from src.get_all import *
import re
from dotenv import load_dotenv
from discord.ext import commands

from src.recommend_cog import RecommendCog
from src.utils import searchSong
from src.song_queue_cog import SongQueueCog

load_dotenv('.env')
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
client = commands.Bot(command_prefix='/', intents=intents)
"""
Function that gets executed once the bot is initialized
"""


@client.event
async def on_ready():
    await SongQueueCog.setup(client)
    await RecommendCog.setup(client)
    BotState.logger = logging.getLogger("discord")

"""
Function that is executed once any message is received by the bot
"""


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    options = set()

    if message.channel.name == 'general':
        user_message = str(message.content)
        await client.process_commands(message)


"""
Start the bot
"""
client.run(TOKEN)
