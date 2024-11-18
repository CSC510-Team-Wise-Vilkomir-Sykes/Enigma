"""
bot.py

This module initializes and runs a Discord bot with multiple cogs, handling song
recommendations,
song queueing, and voice state updates. It configures the bot’s command prefix,
loads essential cogs, and defines event handlers for bot readiness,
incoming messages, and voice state changes.

Environment Variables:
    - DISCORD_TOKEN: The bot token used to authenticate with Discord, loaded from
    a .env file.

Modules:
    - BotState: Manages the state of the bot, including logging and audio playback
    control.
    - RecommendCog: A cog that provides song recommendation and polling commands.
    - SongQueueCog: A cog that handles song queueing operations.
    - searchSong: Utility function for song search.
"""
import asyncio
import logging
import sqlite3

from src.bot_state import BotState
import discord
import os

from dotenv import load_dotenv
from discord.ext import commands

from src.recommend_cog import RecommendCog
from src.song_queue_cog import SongQueueCog

import schedule
from src.scraper import initial_scrape, update_charts

from src.eda import get_top_songs, get_top_artists, get_longest_charting_songs

# Load environment variables from .env file
load_dotenv(".env")
TOKEN = os.getenv("DISCORD_TOKEN")

# Configure intents and create bot instance with command prefix "/"
intents = discord.Intents.all()
client = commands.Bot(command_prefix="/", intents=intents)


# Background task for scheduling
async def schedule_task():
    while True:
        schedule.run_pending()
        await asyncio.sleep(3600)  # Check every hour for scheduled tasks


# Command to start the bot's update scheduler


@client.event
async def on_ready():
    """
            Triggered when the bot is ready and connected to Discord.

            Loads necessary cogs and initializes the bot's logger for state tracking
            and error reporting.
    """
    print(f'Logged in as {client.user}')
    # Define the scraping schedule (e.g., every day at midnight)
    await initial_scrape()

    # Define the scraping schedule (e.g., every day at midnight)
    schedule.every().day.at("00:00").do(update_charts)
    # Start the background task for scheduling
    client.loop.create_task(schedule_task())

    await SongQueueCog.setup(client)  # Initialize the song queue cog
    await RecommendCog.setup(client)  # Initialize the recommendation cog
    BotState.logger = logging.getLogger("discord")  # Set up bot state logging


@client.event
async def on_message(message):
    """
            Processes incoming messages in Discord.

            Ignores messages from the bot itself and allows command processing for
            messages in the
            "general" channel.

            Args:
                    message (discord.Message): The incoming message from Discord.
            """
    if message.author == client.user:
        return  # Ignore messages sent by the bot itself
    options = set()

    # Only process commands in the "general" channel
    if message.content.startswith('!top_songs'):
        df = get_top_songs(sqlite3.connect("../songs.db"))
        response = "Top 10 Popular Songs:\n" + "\n".join(
            f"{i + 1}. {row['title']} by {row['artist']} ({row['chart_name']})" for
            i, row in
            df.iterrows()
        )
        if len(message.content.split(" ")) > 1 and message.content.split(" ")[
            1] == "add":
            for i, row in df.iterrows():
                BotState.song_queue.insert(-1, row['title'])
        await message.channel.send(response)

    elif message.content.startswith('!top_artists'):
        df = get_top_artists(sqlite3.connect("../songs.db"))
        response = "Top 10 Artists by Frequency:\n" + "\n".join(
            f"{i + 1}. {row['artist']}: {row['count']} songs" for i, row in
            df.iterrows()
        )
        await message.channel.send(response)

    elif message.content.startswith('!longest_charting'):
        df = get_longest_charting_songs(sqlite3.connect("../songs.db"))
        response = "Longest-Charting Songs:\n" + "\n".join(
            f"{i + 1}. {row['title']} by {row['artist']} ({row['weeks_on_chart']} "
			f"weeks)"
            for i,
            row
            in df.iterrows()
        )
        if len(message.content.split(" ")) > 1 and message.content.split(" ")[
            1] == "add":
            for i, row in df.iterrows():
                BotState.song_queue.insert(-1, row['title'])
        await message.channel.send(response)
    user_message = str(message.content)
    await client.process_commands(message)  # Process commands issued in messages


@client.event
async def on_voice_state_update(member, before, after):
    """
            Handles voice state changes to manage bot audio playback.

            Pauses or stops playback when the bot moves between voice channels or
            disconnects.

            Args:
                    member (discord.Member): The member whose voice state changed.
                    before (discord.VoiceState): The member's previous voice state.
                    after (discord.VoiceState): The member's current voice state.
            """

    # Check if the member joining/leaving is the bot
    if member is member.guild.me:
        voice_client = member.guild.voice_client
        if after.channel is None or before.channel is None:
            BotState.stop(
                voice_client)  # Stop playback if bot leaves a voice channel
        elif before.channel is not after.channel:
            BotState.pause(voice_client)  # Pause playback if bot switches channels


# Start the bot using the provided token from environment variables
client.run(TOKEN)
