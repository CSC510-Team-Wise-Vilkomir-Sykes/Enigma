"""
This file is responsible for all bot commands regarding songs such /poll for generating recommendations,
/next_song for playing next song and so on
"""
import discord
from src.bot_state import BotState
from src.get_all import *
from dotenv import load_dotenv
from discord.ext import commands

from src.song import Song
from src.utils import searchSong, random_25
import yt_dlp as youtube_dl

# Suppress noise from yt-dlp
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
	'format': 'bestaudio/best',
	'extractaudio': True,
	'noplaylist': True,
	'keepvideo': False,
	'postprocessors': [{
		'key': 'FFmpegExtractAudio',
		'preferredcodec': 'opus',
		'preferredquality': '192'
	}]
}

ffmpeg_options = {
	'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
	'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class SongQueueCog(commands.Cog):
	"""
	Cog for bot that handles all commands related to song queues
	"""

	def __init__(self, bot):
		self.bot = bot

	@commands.command(name='join', help='Joins the voice channel of the user')
	async def join(self, ctx):
		# Check if the user is in a voice channel

		if ctx.author.voice and ctx.author.voice.channel:
			user_channel = ctx.author.voice.channel
			bot_voice_state = ctx.guild.voice_client

			# Check if the bot is already in a voice channel
			if bot_voice_state:
				if bot_voice_state.channel == user_channel:
					await ctx.send(f"I am already in this voice channel ({user_channel.name})")
					BotState.logger.info(
						f"ENIGMA: ({ctx.author.name} /join) Ignored (already in voice channel {user_channel.name})"
					)
				else:
					# Move to the new channel
					await bot_voice_state.move_to(user_channel)
					await ctx.send(f"Switched to voice channel: {user_channel.name}")
					BotState.logger.info(
						f"ENIGMA: ({ctx.author.name} /join) Switched to voice channel {user_channel.name}"
					)
			else:
				# Join the user's voice channel
				await user_channel.connect()
				await ctx.send(f"Joined voice channel: {user_channel.name}")
				BotState.logger.info(
					f"ENIGMA: ({ctx.author.name} /join) Joined voice channel {user_channel.name}"
				)

		else:
			await ctx.send("Please join a voice channel before executing /join")
			BotState.logger.info(
				f"ENIGMA: ({ctx.author.name} /join) Ignored (not in voice channel)"
			)

	@commands.command(name='leave', help='Leaves the voice channel')
	async def leave(self, ctx):
		bot_voice_state = ctx.guild.voice_client

		if bot_voice_state and bot_voice_state.is_connected():
			# Disconnect from the voice channel
			left_name = bot_voice_state.channel.name

			# Stop audio stream if there is one
			if bot_voice_state.is_playing():
				bot_voice_state.stop()
			BotState.current_song_playing = None

			await bot_voice_state.disconnect()
			await ctx.send(f"Left voice channel: {left_name}")
			BotState.logger.info(
				f"ENIGMA: ({ctx.author.name} /leave) Left voice channel {left_name}"
			)
		else:
			# Ignore (not connected to a voice channel)
			await ctx.send("I am currently not connected to a voice channel")
			BotState.logger.info(
				f"ENIGMA: ({ctx.author.name} /leave) Ignored (not connected to a voice channel)"
			)

	"""
		Function to stop playing the music
	"""

	@commands.command(name='pause', help='Pauses the song')
	async def pause(self, ctx):
		voice_client = ctx.message.guild.voice_client
		if voice_client:
			if BotState.current_song_playing is not None:
				if not voice_client.is_paused():
					voice_client.pause()
					await ctx.send("Pausing music")
					BotState.logger.info(
						f"ENIGMA: ({ctx.author.name} /pause) Paused music"
					)
				else:
					await ctx.send("I am already paused")
					BotState.logger.info(
						f"ENIGMA: ({ctx.author.name} /pause) Ignored (already paused)"
					)
			else:
				await ctx.send("I am currently not playing anything")
				BotState.logger.info(
					f"ENIGMA: ({ctx.author.name} /pause) Ignored (not playing music)"
				)
		else:
			await ctx.send("I am currently not connected to a voice channel")
			BotState.logger.info(
				f"ENIGMA: ({ctx.author.name} /pause) Ignored (not connected to a voice channel)"
			)

	"""
	Function for handling resume capability
	"""

	@commands.command(name='unpause', help='unpauses the song')
	async def unpause(self, ctx):
		voice_client = ctx.message.guild.voice_client
		if voice_client:
			if BotState.current_song_playing is not None:
				if voice_client.is_paused():
					voice_client.resume()
					await ctx.send("Resuming music")
					BotState.logger.info(
						f"ENIGMA: ({ctx.author.name} /unpause) Paused music"
					)
				else:
					await ctx.send("I am already playing music")
					BotState.logger.info(
						f"ENIGMA: ({ctx.author.name} /unpause) Ignored (already playing music)"
					)
			else:
				await ctx.send("I am currently not playing anything")
				BotState.logger.info(
					f"ENIGMA: ({ctx.author.name} /unpause) Ignored (not playing music)"
				)
		else:
			await ctx.send("I am currently not connected to a voice channel")
			BotState.logger.info(
				f"ENIGMA: ({ctx.author.name} /unpause) Ignored (not connected to a voice channel)"
			)

	"""
	Function for playing a custom song
	"""

	@commands.command(name='queue', help='queue a custom song')
	async def queue(self, ctx, *, query):
		if query and query.strip():  # check for empty queries
			BotState.song_queue.append(Song(query))
			await ctx.send(f"Adding song to end of queue: {query}")
			BotState.logger.info(
				f"ENIGMA: ({ctx.author.name} /queue) Queued song query '{query}'"
			)
		else:
			await ctx.send("Please specify a youtube query that you would like to queue")
			BotState.logger.info(
				f"ENIGMA: ({ctx.author.name} /queue) Ignored (missing query)"
			)

	@commands.command(name='insert', help='insert a custom song')
	async def insert(self, ctx, *, idx, query):
		# users will assume queue index starts at 1, not 0
		idx = int(idx) - 1

		# check for empty queries
		if query and query.strip():
			BotState.song_queue.insert(idx, Song(query))
			await ctx.send("Adding song to end of queue:")
			BotState.logger.info(
				f"ENIGMA: ({ctx.author.name} /insert) Inserted song query '{query}' at position {idx}"
			)
		else:
			await ctx.send("Please specify a youtube query that you would like to queue")
			BotState.logger.info(
				f"ENIGMA: ({ctx.author.name} /insert) Ignored (missing query)"
			)

	"""
	Helper function for playing song on the voice channel
	"""

	async def play_song(self, ctx, song):
		voice_client = ctx.message.guild.voice_client
		if voice_client:
			# Search for the song on YouTube
			info = ytdl.extract_info(f"ytsearch:{song}", download=False)['entries'][0]
			url = info['url']

			if voice_client.is_playing():
				voice_client.stop()
				BotState.logger.info(
					f"ENIGMA: Terminating current song {BotState.current_song_playing}"
				)

			# Play the audio stream
			ctx.voice_client.play(discord.FFmpegPCMAudio(url, **ffmpeg_options),
								  after=lambda _: self.on_play_query_end(ctx))
			BotState.current_song_playing = song

			await ctx.send(f"Now playing: **{song}**")
			BotState.logger.info(
				f"ENIGMA: Playing {song}"
			)
		else:
			await ctx.send("I am currently not connected to a voice channel")
			BotState.logger.info(
				f"ENIGMA: Ignored (not connected to a voice channel)"
			)

	async def on_play_query_end(self, ctx):
		await ctx.send(f"Finished playing {BotState.current_song_playing}")
		BotState.logger.info(f"ENIGMA: Finished playing {BotState.current_song_playing}")
		await self.next(ctx)


	"""
	Function to play the next song in the queue
	"""

	@commands.command(name='next', help='Immediately jump to the next song in the queue')
	async def next(self, ctx):
		if len(BotState.song_queue) == 0: # Check that there's a song in the queue
			await ctx.send(f"Please add a song to the queue first")
			BotState.logger.info(
				f"ENIGMA: ({ctx.author.name} /next) Ignored (empty queue)"
			)
		else:
			next_song = BotState.song_queue.pop(0)
			await self.play_song(ctx, next_song)

	"""
	Function to display all the songs in the queue, as well as currently playing
	"""

	@commands.command(name='view',
					  help='Show active queue of recommendations')
	async def view(self, ctx):
		msg = ""
		if BotState.current_song_playing is not None:

			voice_client = ctx.message.guild.voice_client
			if voice_client.is_paused():
				pause_str = " **[PAUSED]**"
			else:
				pause_str = ""

			msg += f"Now playing: {BotState.current_song_playing}{pause_str}\n\n"
		else:
			msg += "Currently not playing anything\n\n"

		if len(BotState.song_queue) == 0:
			msg += "No songs in queue. Try /queue <query> to get started"
		else:
			msg += "Current Queue:\n"
			for i, song in enumerate(BotState.song_queue, start=1):
				msg += f"{i}. {song}\n"

		await ctx.send(msg)

		BotState.logger.info(
			f"ENIGMA: ({ctx.author.name} /view) Acknowledged"
		)

	"""
	Function to shuffle songs in the queue
	"""

	@commands.command(name='shuffle', help='To shuffle songs in queue')
	async def shuffle(self, ctx):
		if len(BotState.song_queue) == 0:
			await ctx.send(f"No songs in queue. Try /queue <query> to get started")
		else:
			random.shuffle(BotState.song_queue)
			await ctx.send(f"Shuffled! Do /view to see the current queue")

		BotState.logger.info(
			f"ENIGMA: ({ctx.author.name} /shuffle) Acknowledged"
		)

	@staticmethod
	async def setup(client):
		await client.add_cog(SongQueueCog(client))
