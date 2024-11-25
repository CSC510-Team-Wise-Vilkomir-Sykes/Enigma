"""
bot.py

This module initializes and runs a Discord bot with multiple cogs for handling song recommendations, queueing,
and voice state updates. It configures the bot's command prefix, loads essential cogs, and defines event handlers
for bot readiness, incoming messages, and voice state changes.

**Environment Variables**:
- `DISCORD_TOKEN`: The bot token used to authenticate with Discord, loaded from a `.env` file.

**Modules**:
1. `BotState`: Manages the state of the bot, including logging and audio playback control.
2. `RecommendCog`: A cog that provides song recommendation and polling commands.
3. `SongQueueCog`: A cog that handles song queueing operations.
4. `searchSong`: Utility function for song search.

**Why**: Provides a central entry point to initialize and manage the bot's functionality, enabling music-related
features and responsive user interactions on Discord.

**How**:
- Define event handlers like `on_ready`, `on_message`, and `on_voice_state_update`.
- Load cogs for modular functionality.
- Authenticate using a Discord bot token.

"""

import logging
import os
from dotenv import load_dotenv
from discord.ext import commands
import discord

from src.bot_state import BotState
from src.recommend_cog import RecommendCog
from src.song_queue_cog import SongQueueCog
from src.utils import searchSong

# Load environment variables from a `.env` file
load_dotenv(".env")
TOKEN = os.getenv("DISCORD_TOKEN")

# Configure bot intents and create an instance of the bot with the command prefix "/"
intents = discord.Intents.all()
client = commands.Bot(command_prefix="/", intents=intents)


@client.event
async def on_ready():
	"""
	Event triggered when the bot is ready and connected to Discord.

	**What**:
	- Initializes the bot by loading essential cogs.
	- Sets up logging for state tracking and error reporting.

	**Why**: Ensures the bot is fully prepared for interaction, with all necessary functionality initialized.

	**How**:
	- Load `SongQueueCog` and `RecommendCog` to handle music queueing and recommendations.
	- Log the bot's readiness for debugging or tracking purposes.
	"""
	await SongQueueCog.setup(client)  # Initialize the song queue cog
	await RecommendCog.setup(client)  # Initialize the recommendation cog
	BotState.logger = logging.getLogger("discord")  # Set up bot state logging
	print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
	"""
	Processes incoming messages on Discord.

	**What**:
	- Ignores messages sent by the bot itself.
	- Processes commands in channels whose names start with "general".

	**Why**:
	- Focuses bot functionality on specific channels, preventing interference from non-command messages.

	**How**:
	- Check if the message originates from the bot.
	- Ensure the channel name starts with "general" before processing commands.

	Args:
		message (discord.Message): The incoming message from Discord.
	"""
	if message.author == client.user:
		return  # Ignore messages sent by the bot itself

	# Process commands only in channels that start with "general"
	if message.channel.name.startswith("general"):
		await client.process_commands(message)  # Process commands issued in messages


@client.event
async def on_voice_state_update(member, before, after):
	"""
	Handles changes in voice states to manage audio playback for the bot.

	**What**:
	- Stops playback if the bot disconnects from a voice channel.
	- Pauses playback if the bot switches voice channels.

	**Why**:
	- Ensures smooth audio transitions and avoids playback issues when the bot's voice state changes.

	**How**:
	- Detect whether the bot is leaving or switching channels.
	- Use `BotState` to stop or pause playback accordingly.

	Args:
		member (discord.Member): The member whose voice state changed.
		before (discord.VoiceState): The member's previous voice state.
		after (discord.VoiceState): The member's current voice state.
	"""
	if member is member.guild.me:
		voice_client = member.guild.voice_client
		if after.channel is None or before.channel is None:
			BotState.stop(voice_client)  # Stop playback if bot leaves a voice channel
		elif before.channel is not after.channel:
			BotState.pause(voice_client)  # Pause playback if bot switches channels


# Start the bot using the provided token from environment variables
client.run(TOKEN)
