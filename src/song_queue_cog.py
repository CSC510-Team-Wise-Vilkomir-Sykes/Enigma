"""
This file is responsible for all bot commands regarding songs such /poll for generating recommendations,
/next_song for playing next song and so on
"""
import discord
from src.bot_state import BotState
from src.get_all import *
from dotenv import load_dotenv
from discord.ext import commands
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
			if voice_client.is_playing():
				if not voice_client.is_paused():
					await voice_client.pause()
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
			if voice_client.is_playing():
				if voice_client.is_paused():
					await voice_client.resume()
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
	async def queue(self, ctx, *, song_name):
		voice_client = ctx.message.guild.voice_client



	"""
	Helper function for playing song on the voice channel
	"""

	@staticmethod
	async def play_song(ctx, query):
		# Search for the song on YouTube
		info = ytdl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
		url = info['url']

		# Play the audio stream
		ctx.voice_client.play(discord.FFmpegPCMAudio(url, **ffmpeg_options),
							  after=lambda e: print(f'Finished playing: {e}'))

		await ctx.send(f"Now playing: **{info['title']}**")

	"""
	Helper function to handle empty song queue
	"""

	async def handle_empty_queue(self, ctx):
		# TODO: Refactor without Song_Queue data structure
		return False

	"""
	Function to play the next song in the queue
	"""

	@commands.command(name='next_song', help='To play next song in queue')
	async def next_song(self, ctx):
		empty_queue = await self.handle_empty_queue(ctx)
		if not empty_queue:
			await self.play_song(BotState.song_queue[0], ctx)

	"""
	Function to play the previous song in the queue
	"""

	@commands.command(name='prev_song', help='To play prev song in queue')
	async def play(self, ctx):
		empty_queue = await self.handle_empty_queue(ctx)
		if not empty_queue:
			await self.play_song(BotState.song_queue[0], ctx)

	"""
	Function to pause the music that is playing
	"""

	@commands.command(name='pause', help='This command pauses the song')
	async def pause(self, ctx):
		voice_client = ctx.message.guild.voice_client
		if voice_client.is_playing():
			await voice_client.pause()
		else:
			await ctx.send("The bot is not playing anything at the moment.")

	"""
	Function to display all the songs in the queue
	"""

	@commands.command(name='queue',
					  help='Show active queue of recommendations')
	async def queue(self, ctx):
		empty_queue = await self.handle_empty_queue(ctx)
		if not empty_queue:
			queue, index = BotState.song_queue, 0
			await ctx.send("Queue of recommendations: ")
			for i in range(len(queue)):
				if i == index:
					await ctx.send("Currently Playing: " + queue[i])
				else:
					await ctx.send(queue[i])

	"""
	Function to shuffle songs in the queue
	"""

	@commands.command(name='shuffle', help='To shuffle songs in queue')
	async def shuffle(self, ctx):
		empty_queue = await self.handle_empty_queue(ctx)
		if not empty_queue:
			random.shuffle(BotState.song_queue)
			await ctx.send("Playlist shuffled")

	"""
	Function to add custom song to the queue
	"""

	@commands.command(name='add_song', help='To add custom song to the queue')
	async def add_song(self, ctx):
		user_message = str(ctx.message.content)
		song_name = user_message.split(' ', 1)[1]
		BotState.song_queue.append(song_name)
		await ctx.send("Song added to queue")

	@staticmethod
	async def setup(client):
		await client.add_cog(SongQueueCog(client))
