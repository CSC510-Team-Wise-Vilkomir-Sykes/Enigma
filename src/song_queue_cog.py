"""
This file is responsible for all bot commands regarding songs such /poll for generating recommendations,
/next_song for playing next song and so on
"""
import discord
from discord.ext.commands import bot

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
			voice_client = ctx.guild.voice_client

			# Check if the bot is already in a voice channel
			if BotState.is_in_voice_channel():
				if voice_client.channel == user_channel:
					BotState.log_and_send(ctx, f"I am already in this voice channel ({user_channel.name})")
				else:
					# Move to the new channel
					await voice_client.move_to(user_channel)
					BotState.log_and_send(ctx, f"Switched to voice channel: {user_channel.name}")
			else:
				# Join the user's voice channel
				await user_channel.connect()
				await ctx.send(f"Joined voice channel: {user_channel.name}")
				BotState.log_and_send(ctx, f"Joined voice channel: {user_channel.name}")

		else:
			BotState.log_and_send(ctx, "Please join a voice channel before executing /join")

	@commands.command(name='leave', help='Leaves the voice channel')
	async def leave(self, ctx):
		voice_client = ctx.guild.voice_client

		if BotState.is_in_voice_channel():
			left_name = voice_client.channel.name

			await voice_client.disconnect()

			BotState.log_and_send(ctx, f"Left voice channel: {left_name}")
		else:
			BotState.log_and_send(ctx, "I am currently not connected to a voice channel")

	"""
		Function to stop playing the music
	"""

	@commands.command(name='pause', help='Pauses the song')
	async def pause(self, ctx):
		voice_client = ctx.message.guild.voice_client
		if voice_client:
			if BotState.is_in_use():
				if not BotState.is_paused():
					BotState.pause(voice_client)
					BotState.log_and_send(ctx, "Pausing music")
				else:
					BotState.log_and_send(ctx, "I am already paused")
			else:
				BotState.log_and_send(ctx, "I am currently not playing anything")
		else:
			BotState.log_and_send(ctx, "I am currently not connected to a voice channel")

	"""
	Function for handling resume capability
	"""

	@commands.command(name='unpause', help='unpauses the song')
	async def unpause(self, ctx):
		voice_client = ctx.message.guild.voice_client
		if voice_client:
			if BotState.is_in_use():
				if not BotState.is_paused():
					BotState.unpause(voice_client)
					BotState.log_and_send(ctx, "Unpausing music")
				else:
					BotState.log_and_send(ctx, "I am already unpaused")
			else:
				BotState.log_and_send(ctx, "I am currently not playing anything")
		else:
			BotState.log_and_send(ctx, "I am currently not connected to a voice channel")

	"""
	Function for playing a custom song
	"""

	@commands.command(name='queue', help='queue a custom song')
	async def queue(self, ctx, *, query):
		song = self.ensure_song(ctx, query)
		if song is not None:
			# remember that commands expect queue idx to start at 1
			if self.insert_song(ctx, len(BotState.song_queue) + 1, song):
				BotState.log_and_send(ctx, f"Queued song: {song}")

	@commands.command(name='insert', help='insert a custom song')
	async def insert(self, ctx, *, idx, query):
		song = self.ensure_song(ctx, query)
		if song is not None:
			if self.insert_song(ctx, idx, song):
				BotState.log_and_send(ctx, f"Inserted song {song} as track number {idx}")

	@commands.command(name="insertfront", help="insert a custom song at the front")
	async def insertfront(self, ctx, *, query):
		# remember that commands expect queue idx to start at 1
		await self.insert(ctx, 1, query)

	@staticmethod
	def insert_song(ctx, idx, song):
		idx = SongQueueCog.ensure_insert_number(ctx, idx)
		if idx is not None:
			BotState.song_queue.insert(idx, song)
			return True
		return False

	@staticmethod
	def delete_track(ctx, idx):
		idx = SongQueueCog.ensure_track_number(ctx, idx)
		if idx is not None:
			removed_song = BotState.song_queue.pop(idx)
			return removed_song
		return None

	@staticmethod
	def ensure_song(ctx, query):
		query = query.strip()
		if query:
			return Song(query)
		else:
			BotState.log_and_send(ctx, "Please enter a song")
			return None

	@staticmethod
	def ensure_track_number(ctx, idx):
		try:
			safe_idx = int(idx) - 1
			if safe_idx < 0 or safe_idx >= len(BotState.song_queue):
				raise ValueError
			return safe_idx
		except ValueError:
			BotState.log_and_send(ctx, f'"{idx}" is not a valid track number')
			return None

	@staticmethod
	def ensure_insert_number(ctx, idx):
		try:
			safe_idx = int(idx) - 1
			if safe_idx < 0 or safe_idx > len(BotState.song_queue):
				raise ValueError
			return safe_idx
		except ValueError:
			BotState.log_and_send(ctx, f'"{idx}" is not a valid track number')
			return None


	"""
	Helper function for playing song on the voice channel
	"""

	def play_song(self, ctx, song):
		voice_client = ctx.message.guild.voice_client
		if voice_client:
			# Search for the song on YouTube
			info = ytdl.extract_info(f"ytsearch:{song}", download=False)['entries'][0]
			url = info['url']

			if voice_client.is_playing():
				voice_client.stop()
				BotState.log_command(ctx, f"Terminating current song {BotState.current_song_playing}")

			# Play the audio stream
			ctx.voice_client.play(discord.FFmpegPCMAudio(url, **ffmpeg_options),
								  after=lambda _: self.on_play_query_end(ctx))
			BotState.current_song_playing = song

			BotState.log_and_send(ctx, f"Now playing: **{song}**")
		else:
			BotState.log_and_send(ctx, "I am currently not connected to a voice channel")

	async def on_play_query_end(self, ctx):
		BotState.log_and_send(ctx, f"Finished playing {BotState.current_song_playing}")
		BotState.stop(ctx.guild.voice_client)
		if len(BotState.song_queue) > 0:
			self.play_next_song(ctx)


	"""
	Function to play the next song in the queue
	"""

	@commands.command(name='next', help='Immediately jump to the next song in the queue')
	async def next(self, ctx):
		self.play_next_song(ctx)

	def play_next_song(self, ctx):
		if len(BotState.song_queue) == 0:
			BotState.log_and_send(ctx, f"Please add a song to the queue first")
		else:
			next_song = BotState.song_queue.pop(0)
			self.play_song(ctx, next_song)

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

		BotState.log_command(ctx, "Acknowledged")

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

		BotState.log_command(ctx, "Acknowledged")

	@commands.command(name='jumpto', help='Jump to a track number')
	async def jumpto(self, ctx, *, idx):
		safe_idx = self.ensure_track_number(ctx, idx)

		if safe_idx is not None:
			# We discard all the songs before idx
			BotState.song_queue = BotState.song_queue[safe_idx:]
			BotState.log_and_send(ctx, f"Jumped to track number {idx} in the queue")

	@commands.command(name='move', help='Move the song at the given track number in a different position in the queue')
	async def move(self, ctx, *, src_idx, dest_idx):
		# dest_idx is ensured as a track number (0 < idx < size) and not as an insertion number (0 < idx <= size)
		# this is because when we can only move it to a maximum index of size-1

		safe_dest_idx = self.ensure_track_number(ctx, dest_idx)
		if safe_dest_idx is not None:
			moved_song = self.delete_track(ctx, src_idx)
			if moved_song is not None:
				# we need to pass in dest_idx again, not safe_dest_idx,
				# since safe_dest_idx has been converted to 0-starting idx
				if self.insert_song(ctx, dest_idx, moved_song):
					BotState.log_and_send(f"Moved {moved_song} from track {src_idx} to track {dest_idx}")

	@commands.command(name='remove', help="Removes the song in the queue at the given track number")
	async def remove(self, ctx, *, idx):
		removed_song = self.self.delete_track(ctx, idx)
		if removed_song is not None:
			BotState.log_and_send(ctx, f"Removed {removed_song} (track number {idx})")

	@commands.command(name="movefront", help="Moves a song to the front of the queue")
	async def movefront(self, ctx, *, src_idx):
		# remember that commands expect queue idx to start at 1
		await self.move(ctx, src_idx=src_idx, dest_idx=1)

	@commands.command(name="moveback", help="Moves a song to the back of the queue")
	async def moveback(self, ctx, *, src_idx):
		# remember that commands expect queue idx to start at 1
		await self.move(ctx, src_idx=src_idx, dest_idx=len(BotState.song_queue))

	@staticmethod
	async def setup(client):
		await client.add_cog(SongQueueCog(client))
