"""
song_commands.py

What:
    The `song_commands` module is responsible for handling all Discord bot commands related to song management, including queuing, playback control, and song recommendations. It encapsulates functionalities such as joining voice channels, managing the song queue, controlling playback (play, pause, unpause, skip), and adjusting volume levels. This module leverages Discord's API to provide an interactive and seamless music experience within a Discord server.

Why:
    Music is a fundamental aspect of many Discord communities, enhancing engagement and creating a lively atmosphere. The `song_commands` module empowers users to interact with the bot to manage their listening experience effortlessly. By providing a comprehensive set of commands for song queuing, playback control, and recommendations, the module ensures that users can customize their music preferences, discover new tracks, and maintain an organized queue. This not only enriches the user experience but also fosters a sense of community through shared musical tastes.

How:
    - **Joining and Leaving Voice Channels**: Users can command the bot to join or leave their current voice channel, ensuring that the music playback is aligned with the user's location within the server.

    - **Managing the Song Queue**: Through commands like `/queue`, `/insert`, `/remove`, and `/shuffle`, users can add, insert, remove, and shuffle songs in the queue. These functionalities allow for dynamic and personalized playlist management.

    - **Playback Control**: Commands such as `/pause`, `/unpause`, `/next`, and `/replay` provide users with control over the music playback, enabling them to manage the listening flow according to their preferences.

    - **Volume Adjustment**: The `/volume` command allows users to adjust the playback volume, ensuring that the audio levels meet their comfort and situational needs.

    - **Recommendations and Polling**: Integrating with the `RecommendCog`, commands like `/poll` facilitate song recommendations based on user preferences, enhancing the discovery of new music tailored to the community's tastes.

Example Use Cases:
    1. **Collaborative Playlist Creation**: Multiple users can add and manage songs in the queue, creating a collaborative playlist that reflects the group's collective music preferences.

    2. **Interactive Music Sessions**: During events or gaming sessions, users can control the music playback, ensuring that the audio complements the activity seamlessly.

    3. **Personalized Music Discovery**: By utilizing the polling and recommendation features, users can discover new songs that align with their existing tastes, enhancing their listening experience.

Classes:
    SongQueueCog(commands.Cog):
        A Discord bot cog that manages song-related commands, including joining/leaving voice channels, managing the song queue, controlling playback, and adjusting volume levels.

Functions:
    - join(ctx):
        Joins the voice channel that the user is currently in. If the bot is already in a different voice channel, it moves to the user's channel.

    - leave(ctx):
        Forces the bot to leave its current voice channel.

    - pause(ctx):
        Pauses the currently playing song.

    - unpause(ctx):
        Unpauses the currently paused song.

    - queue(ctx, *, query):
        Adds a song to the end of the queue based on the provided query.

    - insert(ctx, *, params):
        Inserts a song into a specified position in the queue.

    - insertfront(ctx, *, query):
        Inserts a song at the front of the queue.

    - next(ctx):
        Immediately skips to the next song in the queue.

    - view(ctx):
        Displays the current queue and the song that is currently playing.

    - shuffle(ctx):
        Shuffles all the songs in the queue.

    - jumpto(ctx, *, idx):
        Jumps to a specific track number in the queue.

    - move(ctx, *, params):
        Moves a song from one position to another within the queue.

    - remove(ctx, *, idx):
        Removes a song from the queue based on its track number.

    - movefront(ctx, *, src_idx):
        Moves a song to the front of the queue.

    - moveback(ctx, *, src_idx):
        Moves a song to the back of the queue.

    - replay(ctx):
        Replays the currently playing song once after it ends.

    - replaynow(ctx):
        Immediately restarts the currently playing song.

    - volume(ctx, volume: int = -1):
        Adjusts the playback volume to the specified level (0-100).

Dependencies:
    - discord.py: For interacting with the Discord API, handling commands, and managing voice connections.
    - asyncio: For managing asynchronous operations, especially related to audio playback and reaction handling.
    - yt_dlp: For extracting audio information from YouTube links.
    - pandas: For managing song data within DataFrames.
    - dotenv: For loading environment variables.
    - BotState: A custom module to maintain the current state of the bot, including the song queue, playback status, and volume levels.
    - utils: Contains helper functions such as `searchSong` and `random_25` for song searching and random selection.
    - Song: The `Song` class from the `song` module, representing individual music tracks.

Usage:
    To integrate the `SongQueueCog` into your Discord bot, add it to your bot instance as shown below. This will enable all song-related commands, allowing users to manage and control music playback within the Discord server.

    Example:
        ```python
        from discord.ext import commands
        from song_commands import SongQueueCog

        bot = commands.Bot(command_prefix="/")
        bot.add_cog(SongQueueCog(bot))
        bot.run('YOUR_BOT_TOKEN')
        ```

Notes:
    - Ensure that all dependencies are properly installed and configured in your project environment.
    - The bot requires appropriate permissions to join and interact within voice channels.
    - The `BotState` module should be properly implemented to manage the state across different commands and sessions.
    - The `yt_dlp` library is used for extracting audio streams from YouTube; ensure compliance with YouTube's terms of service when using this functionality.
    - Volume levels are normalized between 0.0 and 1.0 internally, corresponding to 0-100% for user interactions.
    - Error handling is implemented to manage invalid inputs and unexpected states, enhancing the robustness of the bot.

"""

import asyncio
import random

import discord


from src.bot_state import BotState
from discord.ext import commands

from src.song import Song
import yt_dlp as youtube_dl

# Suppress noise from yt-dlp
youtube_dl.utils.bug_reports_message = lambda: ""

ytdl_format_options = {
	"format": "bestaudio/best",
	"extractaudio": True,
	"noplaylist": True,
	"keepvideo": False,
	"postprocessors": [
		{
			"key": "FFmpegExtractAudio",
			"preferredcodec": "opus",
			"preferredquality": "192",
		}
	],
}

ffmpeg_options = {
	"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
	"options": "-vn",
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class SongQueueCog(commands.Cog):
	"""
	What:
		The `SongQueueCog` is a Discord bot cog that manages all song-related commands, including joining/leaving voice channels, managing the song queue, controlling playback, and adjusting volume levels. It provides a comprehensive suite of commands that allow users to interact with the music queue, ensuring a seamless and interactive listening experience within a Discord server.

	Why:
		Managing music playback in a Discord server enhances user engagement and fosters a vibrant community atmosphere. The `SongQueueCog` empowers users to control their listening experience by providing intuitive commands for managing the song queue, controlling playback, and customizing volume levels. This flexibility ensures that the music experience is tailored to the preferences of the community, promoting active participation and enjoyment.

	How:
		- **Voice Channel Management**: Users can command the bot to join or leave their current voice channel, ensuring that music playback aligns with their location within the server.

		- **Song Queue Management**: Commands like `/queue`, `/insert`, `/remove`, `/shuffle`, and `/move` allow users to add, insert, remove, shuffle, and rearrange songs in the queue. These functionalities provide dynamic control over the playlist, enabling collaborative and personalized music selection.

		- **Playback Control**: Commands such as `/pause`, `/unpause`, `/next`, `/replay`, and `/replaynow` offer users the ability to control music playback. These controls ensure that users can manage the flow of music according to their preferences and situational needs.

		- **Volume Adjustment**: The `/volume` command enables users to adjust the playback volume, ensuring that the audio levels are comfortable and appropriate for the environment.

		- **Asynchronous Operations**: Leveraging `asyncio`, the cog handles asynchronous tasks such as waiting for user reactions and managing playback queues without blocking the main event loop, ensuring smooth and responsive interactions.

	Example Use Cases:
		1. **Hosting a Music Session**: During a gaming session or virtual event, users can queue songs, control playback, and adjust volume levels to create an engaging and interactive musical backdrop.

		2. **Collaborative Playlist Building**: Multiple users can add and manage songs in the queue, creating a collaborative playlist that reflects the collective musical tastes of the group.

		3. **Personalized Listening Experience**: Users can manage their own listening preferences by inserting favorite songs, replaying tracks, and adjusting volume levels to suit their personal comfort.

	Classes:
		SongQueueCog(commands.Cog):
			Manages all song-related commands and functionalities, including voice channel management, song queue operations, playback controls, and volume adjustments.

	Functions:
		- __init__(self, bot):
			Initializes the `SongQueueCog` with the Discord bot instance.

		- join(ctx):
			Joins the voice channel that the user is currently in. If the bot is already in a different voice channel, it moves to the user's channel.

		- leave(ctx):
			Forces the bot to leave its current voice channel.

		- pause(ctx):
			Pauses the currently playing song.

		- unpause(ctx):
			Unpauses the currently paused song.

		- queue(ctx, *, query):
			Adds a song to the end of the queue based on the provided query.

		- insert(ctx, *, params):
			Inserts a song into a specified position in the queue.

		- insertfront(ctx, *, query):
			Inserts a song at the front of the queue.

		- insert_song(ctx, idx, song):
			Helper function to insert songs into the queue at a specified index.

		- delete_track(ctx, idx):
			Helper function to delete a song from the queue based on its track number.

		- ensure_song(ctx, query):
			Helper function to validate and convert a query into a `Song` object.

		- ensure_track_number(ctx, idx):
			Helper function to validate and convert a track number from user input.

		- ensure_insert_number(ctx, idx):
			Helper function to validate and convert an insertion number from user input.

		- play_song(ctx, song):
			Helper function to handle the playback of a specified song.

		- on_play_query_end(ctx, error):
			Callback function that runs once a song finishes playing or is terminated, triggering the next song in the queue.

		- next(ctx):
			Immediately skips to the next song in the queue.

		- play_next_song(ctx):
			Helper function to play the next song in the queue.

		- view(ctx):
			Displays the current song queue and the song that is currently playing.

		- shuffle(ctx):
			Shuffles all the songs in the current queue.

		- jumpto(ctx, *, idx):
			Jumps to a specific track number in the queue, discarding all songs before it.

		- move(ctx, *, params):
			Moves a song from one position to another within the queue.

		- remove(ctx, *, idx):
			Removes a song from the queue based on its track number.

		- movefront(ctx, *, src_idx):
			Moves a song to the front of the queue.

		- moveback(ctx, *, src_idx):
			Moves a song to the back of the queue.

		- replay(ctx):
			Replays the currently playing song once after it ends.

		- replaynow(ctx):
			Immediately restarts the currently playing song.

		- volume(ctx, volume: int = -1):
			Adjusts the playback volume to the specified level (0-100).

		- setup(client):
			Registers the `SongQueueCog` with the Discord client.

	Dependencies:
		- discord.py: Facilitates interaction with the Discord API, enabling command handling, voice channel management, and audio playback.
		- asyncio: Manages asynchronous operations, ensuring that the bot remains responsive during tasks such as waiting for user reactions and handling playback queues.
		- yt_dlp: Extracts audio information from YouTube links, enabling the bot to stream audio tracks.
		- pandas: Manages song data within DataFrames for efficient data manipulation and retrieval.
		- dotenv: Loads environment variables from a `.env` file, ensuring secure and configurable deployment.
		- BotState: A custom module that maintains the current state of the bot, including the song queue, playback status, and volume levels.
		- utils: Provides helper functions such as `searchSong` and `random_25` for song searching and random selection.
		- Song: The `Song` class from the `song` module, representing individual music tracks.

	Usage:
		To utilize the `SongQueueCog` in your Discord bot, integrate it by adding it to your bot instance as demonstrated below. This will enable all song-related commands, allowing users to manage and control music playback within the Discord server.

		Example:
			```python
			from discord.ext import commands
			from song_commands import SongQueueCog

			bot = commands.Bot(command_prefix="/")
			bot.add_cog(SongQueueCog(bot))
			bot.run('YOUR_BOT_TOKEN')
			```

	Notes:
		- Ensure that all dependencies are properly installed and configured in your project environment.
		- The bot requires appropriate permissions to join and interact within voice channels.
		- The `BotState` module should be properly implemented to manage the state across different commands and sessions.
		- The `yt_dlp` library is used for extracting audio streams from YouTube; ensure compliance with YouTube's terms of service when using this functionality.
		- Volume levels are normalized between 0.0 and 1.0 internally, corresponding to 0-100% for user interactions.
		- Error handling is implemented to manage invalid inputs and unexpected states, enhancing the robustness of the bot.

	"""

	def __init__(self, bot):
		"""
		What:
			Initializes the `SongQueueCog` with the provided Discord bot instance, setting up necessary configurations for managing song commands and playback functionalities.

		Why:
			Proper initialization ensures that the cog is correctly integrated with the Discord bot, allowing it to listen for and respond to relevant commands. This setup is essential for maintaining consistent state management and facilitating seamless interactions between users and the bot.

		How:
			- Stores the bot instance for use within the cog.
			- Configures YouTube download options using `yt_dlp`.
			- Sets up FFmpeg options for audio playback.

		Parameters:
			bot (commands.Bot): The Discord bot instance to which this cog is being added.

		Example:
			```python
			bot = commands.Bot(command_prefix="/")
			bot.add_cog(SongQueueCog(bot))
			```
		"""
		self.bot = bot

	@commands.command(name="join", help="Joins the voice channel of the user")
	async def join(self, ctx):
		"""
		What:
			The `/join` command instructs the bot to join the voice channel that the user is currently in. If the bot is already connected to a different voice channel, it will move to the user's channel.

		Why:
			Ensuring that the bot is in the same voice channel as the user allows for synchronized music playback, enhancing the collective listening experience within the server.

		How:
			- Checks if the user is in a voice channel.
			- Determines if the bot is already connected to a voice channel.
			- Joins the user's voice channel or moves from the current channel to the user's channel as necessary.
			- Sends confirmation messages to inform users of the bot's actions.

		Example:
			A user types `/join` while in the "Music Room" voice channel. The bot joins the "Music Room" channel and confirms the action by sending a message like "Joined voice channel: Music Room".

		Parameters:
			ctx (commands.Context): The context of the command invocation, containing information such as the channel, author, and guild.
		"""
		# Check if the user is in a voice channel
		if ctx.author.voice and ctx.author.voice.channel:
			user_channel = ctx.author.voice.channel
			voice_client = ctx.guild.voice_client

			# Check if the bot is already in a voice channel
			if BotState.is_in_voice_channel(voice_client):
				if voice_client.channel == user_channel:
					await BotState.log_and_send(
						ctx,
						f"I am already in this voice channel ({user_channel.name})"
					)
				else:
					# Move to the new channel
					await voice_client.move_to(user_channel)
					await BotState.log_and_send(
						ctx, f"Switched to voice channel: {user_channel.name}"
					)
			else:
				# Join the user's voice channel
				await user_channel.connect()
				await BotState.log_and_send(
					ctx, f"Joined voice channel: {user_channel.name}"
				)

		else:
			await BotState.log_and_send(
				ctx, "Please join a voice channel before executing /join"
			)

	@commands.command(name="leave", help="Leaves the voice channel")
	async def leave(self, ctx):
		"""
		What:
			The `/leave` command instructs the bot to disconnect from its current voice channel, effectively stopping any ongoing music playback.

		Why:
			Allowing users to control the bot's presence in voice channels provides flexibility and ensures that the bot does not occupy channels unnecessarily, especially in dynamic server environments.

		How:
			- Checks if the bot is currently connected to a voice channel.
			- Disconnects from the voice channel if connected.
			- Sends confirmation messages to inform users of the bot's actions.

		Example:
			A user types `/leave`. If the bot is in the "Music Room" channel, it disconnects and sends a message like "Left voice channel: Music Room".

		Parameters:
			ctx (commands.Context): The context of the command invocation, containing information such as the channel, author, and guild.
		"""
		voice_client = ctx.guild.voice_client

		if BotState.is_in_voice_channel(voice_client):
			left_name = voice_client.channel.name
			await voice_client.disconnect()

			await BotState.log_and_send(ctx, f"Left voice channel: {left_name}")
		else:
			await BotState.log_and_send(
				ctx, "I am currently not connected to a voice channel"
			)

	@commands.command(name="pause", help="Pauses the song")
	async def pause(self, ctx):
		"""
		What:
			The `/pause` command pauses the currently playing song in the voice channel.

		Why:
			Providing pause functionality allows users to temporarily halt music playback without disrupting the current queue, enabling them to attend to other tasks or discussions without losing their place in the playlist.

		How:
			- Checks if the bot is connected to a voice channel and if music is currently playing.
			- Pauses the playback if it is not already paused.
			- Sends confirmation messages to inform users of the action taken.

		Example:
			A user types `/pause`. If a song is playing, the bot pauses the music and sends a message like "Pausing music".

		Parameters:
			ctx (commands.Context): The context of the command invocation, containing information such as the channel, author, and guild.
		"""
		voice_client = ctx.message.guild.voice_client
		if voice_client:
			if BotState.is_in_use():
				if not BotState.is_paused():
					BotState.pause(voice_client)
					await BotState.log_and_send(ctx, "Pausing music")
				else:
					await BotState.log_and_send(ctx, "I am already paused")
			else:
				await BotState.log_and_send(ctx,
											"I am currently not playing anything")
		else:
			await BotState.log_and_send(
				ctx, "I am currently not connected to a voice channel"
			)

	@commands.command(name="unpause", help="Unpauses the song")
	async def unpause(self, ctx):
		"""
		What:
			The `/unpause` command resumes playback of a paused song in the voice channel.

		Why:
			Allowing users to resume paused music provides control over the listening experience, enabling them to continue enjoying the playlist without needing to restart songs or queues.

		How:
			- Checks if the bot is connected to a voice channel and if music is currently paused.
			- Unpauses the playback if it is paused.
			- Sends confirmation messages to inform users of the action taken.

		Example:
			A user types `/unpause`. If the music is paused, the bot resumes playback and sends a message like "Unpausing music".

		Parameters:
			ctx (commands.Context): The context of the command invocation, containing information such as the channel, author, and guild.
		"""
		voice_client = ctx.message.guild.voice_client
		if voice_client:
			if BotState.is_in_use():
				if BotState.is_paused():
					BotState.unpause(voice_client)
					await BotState.log_and_send(ctx, "Unpausing music")
				else:
					await BotState.log_and_send(ctx, "I am already unpaused")
			else:
				await BotState.log_and_send(ctx,
                                            "I am currently not playing anything")
		else:
			await BotState.log_and_send(
				ctx, "I am currently not connected to a voice channel"
			)

	@commands.command(name="queue", help="Queue a custom song")
	async def queue(self, ctx, *, query):
		"""
		What:
			The `/queue` command adds a song to the end of the current song queue based on the provided query.

		Why:
			Allowing users to add songs to the queue ensures that the playlist reflects the community's preferences and accommodates dynamic song selection.

		How:
			- Validates and converts the user's query into a `Song` object.
			- Inserts the song at the end of the queue.
			- Sends confirmation messages to inform users that the song has been queued.

		Example:
			A user types `/queue Never Gonna Give You Up`. The bot adds "Never Gonna Give You Up" to the end of the queue and sends a message like "Queued song: Never Gonna Give You Up by Rick Astley".

		Parameters:
			ctx (commands.Context): The context of the command invocation, containing information such as the channel, author, and guild.
			query (str): The search query or name of the song to be added to the queue.
		"""
		song = await self.ensure_song(ctx, query)
		if song is not None:
			# remember that commands expect queue idx to start at 1
			if await self.insert_song(ctx, len(BotState.song_queue) + 1, song):
				await BotState.log_and_send(ctx, f"Queued song: {song}")

	@commands.command(name="insert", help="Insert a custom song")
	async def insert(self, ctx, *, params):
		"""
		What:
			The `/insert` command inserts a song into a specified position within the current song queue based on the provided parameters.

		Why:
			Providing the ability to insert songs at arbitrary positions allows users to prioritize certain tracks or rearrange the playlist to better suit their preferences.

		How:
			- Parses the input parameters to extract the target index and song query.
			- Validates and converts the song query into a `Song` object.
			- Inserts the song at the specified position in the queue.
			- Sends confirmation messages to inform users that the song has been inserted.

		Example:
			A user types `/insert 2 Shape of You`. The bot inserts "Shape of You" at position 2 in the queue and sends a message like "Inserted song Shape of You by Ed Sheeran as track number 2".

		Parameters:
			ctx (commands.Context): The context of the command invocation, containing information such as the channel, author, and guild.
			params (str): A string containing the target index and song query, separated by a space (e.g., "2 Shape of You").
		"""
		idx, query = params.split(" ", maxsplit=1)
		song = await self.ensure_song(ctx, query)
		if song is not None:
			if await self.insert_song(ctx, idx, song):
				await BotState.log_and_send(
					ctx, f"Inserted song {song} as track number {idx}"
				)

	@commands.command(name="insertfront", help="Insert a custom song at the front")
	async def insertfront(self, ctx, *, query):
		"""
		What:
			The `/insertfront` command inserts a song at the very front of the current song queue.

		Why:
			Allowing users to prioritize certain songs by inserting them at the front ensures that important or favorite tracks are played immediately.

		How:
			- Validates and converts the user's query into a `Song` object.
			- Inserts the song at the front of the queue.
			- Sends confirmation messages to inform users that the song has been inserted at the front.

		Example:
			A user types `/insertfront Bohemian Rhapsody`. The bot inserts "Bohemian Rhapsody" at the front of the queue and sends a message like "Inserted song Bohemian Rhapsody by Queen as track number 1".

		Parameters:
			ctx (commands.Context): The context of the command invocation, containing information such as the channel, author, and guild.
			query (str): The search query or name of the song to be inserted at the front of the queue.
		"""
		# remember that commands expect queue idx to start at 1
		await self.insert(ctx, params=f"1 {query}")

	@staticmethod
	async def insert_song(ctx, idx, song):
		"""
		What:
			The `insert_song` helper function inserts a `Song` object into the queue at the specified index.

		Why:
			Encapsulating the insertion logic within a helper function promotes code reusability and ensures consistent handling of song insertions across different commands.

		How:
			- Validates the insertion index.
			- Inserts the song into the queue at the validated index.
			- Returns a boolean indicating the success of the operation.

		Example:
			Inserting a song at position 3: `insert_song(ctx, 3, Song("Imagine", "John Lennon", "Rock"))`

		Parameters:
			ctx (commands.Context): The context of the command invocation.
			idx (int or str): The target index at which to insert the song.
			song (Song): The `Song` object to be inserted into the queue.

		Returns:
			bool: `True` if the insertion was successful, `False` otherwise.
		"""
		idx = await SongQueueCog.ensure_insert_number(ctx, idx)
		if idx is not None:
			BotState.song_queue.insert(idx, song)
			return True
		return False

	@staticmethod
	async def delete_track(ctx, idx):
		"""
		What:
			The `delete_track` helper function removes a song from the queue based on its track number.

		Why:
			Providing a method to delete tracks ensures that users can manage the queue effectively, removing unwanted or unwanted songs to maintain a preferred playlist order.

		How:
			- Validates the track number.
			- Removes the song from the queue at the validated index.
			- Returns the removed `Song` object if successful.

		Example:
			Removing the song at track number 4: `delete_track(ctx, 4)`

		Parameters:
			ctx (commands.Context): The context of the command invocation.
			idx (int or str): The track number of the song to be removed.

		Returns:
			Song or None: The removed `Song` object if the deletion was successful, `None` otherwise.
		"""
		idx = await SongQueueCog.ensure_track_number(ctx, idx)
		if idx is not None:
			removed_song = BotState.song_queue.pop(idx)
			return removed_song
		return None

	@staticmethod
	async def ensure_song(ctx, query):
		"""
		What:
			The `ensure_song` helper function validates and converts a user's query into a `Song` object.

		Why:
			Ensuring that the query is valid and properly formatted is essential for maintaining the integrity of the song queue and preventing errors during playback.

		How:
			- Strips any leading or trailing whitespace from the query.
			- Checks if the query is non-empty.
			- Creates a `Song` object if the query is valid.
			- Sends an error message if the query is invalid.

		Example:
			Valid query: "Shape of You" → `Song("Shape of You")`
			Invalid query: "" → Sends "Please enter a song"

		Parameters:
			ctx (commands.Context): The context of the command invocation.
			query (str): The user's search query or song name.

		Returns:
			Song or None: The created `Song` object if the query is valid, `None` otherwise.
		"""
		query = query.strip()
		if query:
			return Song(query)
		else:
			await BotState.log_and_send(ctx, "Please enter a song")
			return None

	@staticmethod
	async def ensure_track_number(ctx, idx):
		"""
		What:
			The `ensure_track_number` helper function validates and converts a track number from user input into a zero-based index.

		Why:
			Validating track numbers ensures that operations like removing or moving songs in the queue are performed on valid entries, preventing out-of-range errors and maintaining queue integrity.

		How:
			- Attempts to convert the input to an integer.
			- Adjusts for zero-based indexing.
			- Checks if the index is within the valid range of the queue.
			- Sends an error message if the index is invalid.

		Example:
			Valid input: "3" → Returns `2` (zero-based index)
			Invalid input: "0" or "100" (if queue has fewer songs) → Sends '"0" is not a valid track number'

		Parameters:
			ctx (commands.Context): The context of the command invocation.
			idx (int or str): The track number input by the user.

		Returns:
			int or None: The zero-based index if valid, `None` otherwise.
		"""
		try:
			safe_idx = int(idx) - 1
			if safe_idx < 0 or safe_idx >= len(BotState.song_queue):
				raise ValueError
			return safe_idx
		except ValueError:
			await BotState.log_and_send(ctx, f'"{idx}" is not a valid track number')
			return None

	@staticmethod
	async def ensure_insert_number(ctx, idx):
		"""
		What:
			The `ensure_insert_number` helper function validates and converts an insertion number from user input into a zero-based index suitable for inserting into the queue.

		Why:
			Validating insertion numbers ensures that songs are inserted at valid positions within the queue, preventing out-of-range errors and maintaining queue integrity.

		How:
			- Attempts to convert the input to an integer.
			- Adjusts for zero-based indexing.
			- Checks if the index is within the valid range for insertion.
			- Sends an error message if the index is invalid.

		Example:
			Valid input: "1" → Returns `0` (zero-based index)
			Valid input: "5" (if queue has 4 songs) → Returns `4`
			Invalid input: "-1" or "abc" → Sends '"-1" is not a valid track number'

		Parameters:
			ctx (commands.Context): The context of the command invocation.
			idx (int or str): The insertion number input by the user.

		Returns:
			int or None: The zero-based index if valid, `None` otherwise.
		"""
		try:
			safe_idx = int(idx) - 1
			if safe_idx < 0 or safe_idx > len(BotState.song_queue):
				raise ValueError
			return safe_idx
		except ValueError:
			await BotState.log_and_send(ctx, f'"{idx}" is not a valid track number')
			return None

	async def play_song(self, ctx, song):
		"""
		What:
			The `play_song` helper function handles the playback of a specified song within the voice channel.

		Why:
			Encapsulating the playback logic within a helper function ensures consistent handling of audio streams, error management, and state updates, providing a smooth listening experience for users.

		How:
			- Searches for the song on YouTube using `yt_dlp`.
			- Extracts the audio URL and prepares the audio source with FFmpeg options.
			- Manages the playback state, including stopping any currently playing song if necessary.
			- Initiates audio playback in the voice channel.
			- Sends confirmation messages to inform users of the currently playing song.

		Example:
			Playing "Shape of You": `play_song(ctx, Song("Shape of You"))` → Plays the song and sends "Now playing: **Shape of You by Ed Sheeran**"

		Parameters:
			ctx (commands.Context): The context of the command invocation.
			song (Song): The `Song` object representing the song to be played.

		Returns:
			None
		"""
		voice_client = ctx.message.guild.voice_client
		if voice_client:
			# Search for the song on YouTube
			info = ytdl.extract_info(f"ytsearch:{song}", download=False)["entries"][
                0]
			url = info["url"]

			if BotState.is_in_use():
				BotState.stop(voice_client)
				BotState.log_command(
					ctx, f"Terminating current song {BotState.current_song_playing}"
				)

			while BotState.is_in_use():
				# we must wait for the previous song to clean up
				await asyncio.sleep(0.1)

			# Create FFmpeg audio source with applied filters
			audio_source = discord.FFmpegPCMAudio(url, **ffmpeg_options)
			# Apply volume transformation
			audio_source = discord.PCMVolumeTransformer(audio_source, volume=BotState.volume)

			# Play the audio stream
			ctx.voice_client.play(
				audio_source,
				after=lambda error: asyncio.run_coroutine_threadsafe(
					self.on_play_query_end(ctx, error), self.bot.loop
				),
			)
			BotState.current_song_playing = song

			await BotState.log_and_send(ctx, f"Now playing: **{song}**")
		else:
			await BotState.log_and_send(
				ctx, "I am currently not connected to a voice channel"
			)

	async def on_play_query_end(self, ctx, error):
		"""
		What:
			The `on_play_query_end` callback function is invoked once a song finishes playing or is terminated. It handles the transition to the next song in the queue or repeats the current song if looping is enabled.

		Why:
			Managing the end of song playback ensures that the music queue progresses smoothly, automatically playing the next song or repeating as per the user's preferences without requiring manual intervention.

		How:
			- Logs the completion of the current song.
			- Stops the current playback state.
			- Checks if looping is enabled; if so, replays the current song.
			- Otherwise, plays the next song in the queue if available.

		Example:
			After "Shape of You" finishes playing, `on_play_query_end` is called to either replay the song or proceed to the next track in the queue.

		Parameters:
			ctx (commands.Context): The context of the command invocation.
			error (Exception): Any error that occurred during playback.

		Returns:
			None
		"""
		voice_client = ctx.guild.voice_client

		BotState.log_command(ctx, "Finished playing song")
		BotState.stop(voice_client)

		if BotState.is_in_voice_channel(voice_client):
			if BotState.is_looping():
				await self.play_song(ctx, BotState.current_song_playing)
			else:
				if len(BotState.song_queue) > 0:
					await self.play_next_song(ctx)

	@commands.command(
		name="next", help="Immediately jump to the next song in the queue"
	)
	async def next(self, ctx):
		"""
		What:
			The `/next` command immediately skips the currently playing song and moves to the next song in the queue.

		Why:
			Providing a quick way to skip songs enhances user control over the listening experience, allowing them to bypass unwanted tracks without disrupting the entire queue.

		How:
			- Checks if a song is currently playing.
			- Stops the current playback.
			- Initiates playback of the next song in the queue.

		Example:
			A user types `/next` while "Shape of You" is playing. The bot stops "Shape of You" and starts playing the next song in the queue, sending a message like "Now playing: **Blinding Lights by The Weeknd**".

		Parameters:
			ctx (commands.Context): The context of the command invocation.
		"""
		if BotState.is_in_use():
			BotState.stop(ctx.guild.voice_client)
		else:
			await self.play_next_song(ctx)

	async def play_next_song(self, ctx):
		"""
		What:
			The `play_next_song` helper function plays the next song in the queue if one exists.

		Why:
			Automating the transition to the next song ensures a continuous and uninterrupted music playback experience for users.

		How:
			- Checks if there are songs in the queue.
			- Removes the next song from the queue.
			- Initiates playback of the next song using `play_song`.
			- Sends confirmation messages to inform users of the action taken.

		Example:
			If the queue contains "Bohemian Rhapsody" and "Imagine", calling `play_next_song` will remove "Bohemian Rhapsody" from the queue and start playing it, sending "Now playing: **Bohemian Rhapsody by Queen**".

		Parameters:
			ctx (commands.Context): The context of the command invocation.

		Returns:
			None
		"""
		if len(BotState.song_queue) == 0:
			await BotState.log_and_send(ctx, f"Please add a song to the queue first")
		else:
			next_song = BotState.song_queue.pop(0)
			await self.play_song(ctx, next_song)

	@commands.command(name="view",
                      help="Show current queue and currently playing song")
	async def view(self, ctx):
		"""
		What:
			The `/view` command displays the current song queue and indicates which song is currently playing.

		Why:
			Providing visibility into the song queue and playback status allows users to stay informed about the current playlist and upcoming tracks, enhancing transparency and coordination within the server.

		How:
			- Checks if a song is currently playing.
			- Constructs a message detailing the currently playing song and the list of queued songs.
			- Sends the constructed message to the channel.

		Example:
			A user types `/view`. The bot responds with:
			```
			Now playing: Shape of You by Ed Sheeran

			Current Queue:
			1. Bohemian Rhapsody by Queen
			2. Imagine by John Lennon
			```

		Parameters:
			ctx (commands.Context): The context of the command invocation.
		"""
		msg = ""
		if BotState.is_in_use():
			msg += f"Now playing: {BotState.current_song_playing}"

			if BotState.is_paused():
				msg += " **[PAUSED]**"

			if BotState.is_looping():
				msg += " **[LOOPING]**"

			msg += "\n\n"
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

	@commands.command(name="shuffle", help="Shuffle songs in queue")
	async def shuffle(self, ctx):
		"""
		What:
			The `/shuffle` command randomizes the order of songs in the current queue.

		Why:
			Shuffling the queue provides variety and ensures that the listening experience remains fresh and unpredictable, catering to diverse user preferences.

		How:
			- Checks if there are songs in the queue.
			- Randomizes the order of the songs using Python's `random.shuffle`.
			- Sends a confirmation message indicating that the queue has been shuffled.

		Example:
			A user types `/shuffle`. If the queue has multiple songs, the bot shuffles their order and sends a message like "Shuffled! Do /view to see the current queue".

		Parameters:
			ctx (commands.Context): The context of the command invocation.
		"""
		if len(BotState.song_queue) == 0:
			await ctx.send(f"No songs in queue. Try /queue <query> to get started")
		else:
			random.shuffle(BotState.song_queue)
			await ctx.send(f"Shuffled! Do /view to see the current queue")

		BotState.log_command(ctx, "Acknowledged")

	@commands.command(name="jumpto", help="Jump to a specific track number")
	async def jumpto(self, ctx, *, idx):
		"""
		What:
			The `/jumpto` command allows users to jump directly to a specific track number in the queue, discarding all songs that precede it.

		Why:
			Providing the ability to jump to a specific track offers users greater control over the playlist, enabling them to prioritize or revisit particular songs without manually skipping through the queue.

		How:
			- Validates the provided track number.
			- Adjusts the queue by removing all songs before the specified track.
			- Initiates playback of the specified track.

		Example:
			A user types `/jumpto 3`. The bot removes the first two songs from the queue and starts playing the third song, sending a message like "Jumped to track number 3 in the queue".

		Parameters:
			ctx (commands.Context): The context of the command invocation.
			idx (int or str): The track number to jump to.

		Returns:
			None
		"""
		safe_idx = await self.ensure_track_number(ctx, idx)

		if safe_idx is not None:
			# We discard all the songs before idx
			BotState.song_queue = BotState.song_queue[safe_idx:]
			await BotState.log_and_send(
				ctx, f"Jumped to track number {idx} in the queue"
			)

	@commands.command(
		name="move",
		help="Move a song from one position to another in "
             "the queue",
	)
	async def move(self, ctx, *, params):
		"""
		What:
			The `/move` command moves a song from one track number to another within the current queue.

		Why:
			Allowing users to rearrange songs in the queue enhances the ability to prioritize certain tracks, ensuring that favorite or important songs are played in the desired order.

		How:
			- Parses the input parameters to extract the source and destination indices.
			- Validates both indices.
			- Removes the song from the source position and inserts it at the destination position.
			- Sends confirmation messages to inform users of the action taken.

		Example:
			A user types `/move 2 5`. The bot moves the song at track number 2 to track number 5, sending a message like "Moved Imagine by John Lennon from track 2 to track 5".

		Parameters:
			ctx (commands.Context): The context of the command invocation.
			params (str): A string containing the source and destination track numbers, separated by a space (e.g., "2 5").

		Returns:
			None
		"""
		src_idx, dest_idx = params.split(" ", maxsplit=1)

		# dest_idx is ensured as a track number (0 < idx < size) and not as an
        # insertion number (0 < idx <= size)
		# this is because when we can only move it to a maximum index of size-1
		safe_dest_idx = await self.ensure_track_number(ctx, dest_idx)
		if safe_dest_idx is not None:
			moved_song = await self.delete_track(ctx, src_idx)
			if moved_song is not None:
				# we need to pass in dest_idx again, not safe_dest_idx,
				# since safe_dest_idx has been converted to 0-starting idx
				if await self.insert_song(ctx, dest_idx, moved_song):
					await BotState.log_and_send(
						ctx,
						f"Moved {moved_song} from track {src_idx} to track "
                        f"{dest_idx}",
					)

	@commands.command(
		name="remove", help="Remove a song from the queue by track number"
	)
	async def remove(self, ctx, *, idx):
		"""
		What:
			The `/remove` command deletes a song from the queue based on its track number.

		Why:
			Providing the ability to remove unwanted or duplicate songs ensures that the queue remains organized and reflective of the users' current preferences.

		How:
			- Validates the provided track number.
			- Removes the song from the queue at the specified index.
			- Sends confirmation messages to inform users of the removal.

		Example:
			A user types `/remove 3`. The bot removes the third song from the queue and sends a message like "Removed Imagine by John Lennon (track number 3)".

		Parameters:
			ctx (commands.Context): The context of the command invocation.
			idx (int or str): The track number of the song to be removed.

		Returns:
			None
		"""
		removed_song = await self.delete_track(ctx, idx)
		if removed_song is not None:
			await BotState.log_and_send(
				ctx, f"Removed {removed_song} (track number {idx})"
			)

	@commands.command(name="movefront",
                      help="Move a song to the front of the queue")
	async def movefront(self, ctx, *, src_idx):
		"""
		What:
			The `/movefront` command moves a specified song to the front of the queue.

		Why:
			Allowing users to prioritize certain songs by moving them to the front ensures that important tracks are played immediately, enhancing the listening experience.

		How:
			- Validates the provided source track number.
			- Moves the song to the front of the queue using the `/move` command internally.
			- Sends confirmation messages to inform users of the action taken.

		Example:
			A user types `/movefront 4`. The bot moves the fourth song to the front of the queue and sends a message like "Moved Imagine by John Lennon from track 4 to track 1".

		Parameters:
			ctx (commands.Context): The context of the command invocation.
			src_idx (int or str): The track number of the song to be moved to the front.

		Returns:
			None
		"""
		# remember that commands expect queue idx to start at 1
		await self.move(ctx, params=f"{src_idx} 1")

	@commands.command(name="moveback", help="Move a song to the back of the queue")
	async def moveback(self, ctx, *, src_idx):
		"""
		What:
			The `/moveback` command moves a specified song to the back of the queue.

		Why:
			Allowing users to deprioritize certain songs by moving them to the back ensures that less preferred tracks are played later, maintaining an enjoyable and relevant playlist.

		How:
			- Validates the provided source track number.
			- Moves the song to the back of the queue using the `/move` command internally.
			- Sends confirmation messages to inform users of the action taken.

		Example:
			A user types `/moveback 2`. The bot moves the second song to the back of the queue and sends a message like "Moved Bohemian Rhapsody by Queen from track 2 to track 5".

		Parameters:
			ctx (commands.Context): The context of the command invocation.
			src_idx (int or str): The track number of the song to be moved to the back.

		Returns:
			None
		"""
		# remember that commands expect queue idx to start at 1
		await self.move(ctx, params=f"{src_idx} {len(BotState.song_queue)}")

	@commands.command(
		name="replay",
        help="Replay the currently playing song once after it ends"
	)
	async def replay(self, ctx):
		"""
		What:
			The `/replay` command schedules the currently playing song to be replayed once after it finishes.

		Why:
			Replaying a song allows users to listen to their favorite tracks again without manually re-queueing them, enhancing the flexibility and enjoyment of the listening experience.

		How:
			- Checks if a song is currently playing.
			- If looping is not already enabled, inserts the currently playing song at the front of the queue.
			- Sends confirmation messages to inform users of the action taken.

		Example:
			A user types `/replay`. If "Imagine" is currently playing, the bot schedules it to be replayed by adding it to the front of the queue and sends a message like "Got it, I will add this song to the front of the queue again".

		Parameters:
			ctx (commands.Context): The context of the command invocation.

		Returns:
			None
		"""
		if not BotState.is_in_use():
			await BotState.log_and_send(ctx, "I am currently not playing any songs")
		else:
			if BotState.is_looping():
				await BotState.log_and_send(ctx, "I am already set to loop")
			else:
				await self.insert_song(ctx, 1, BotState.current_song_playing)
				await BotState.log_and_send(
					ctx,
                    "Got it, I will add this song to the front of the queue again"
				)

	@commands.command(
		name="replaynow", help="Immediately restart the currently playing song"
	)
	async def replaynow(self, ctx):
		"""
		What:
			The `/replaynow` command immediately restarts the currently playing song.

		Why:
			Allowing users to instantly replay a song ensures that they can enjoy their favorite tracks again without waiting for the queue to cycle through.

		How:
			- Checks if a song is currently playing.
			- Inserts the currently playing song at the front of the queue.
			- Invokes the `/next` command to start playing the song immediately.
			- Sends confirmation messages to inform users of the action taken.

		Example:
			A user types `/replaynow` while "Shape of You" is playing. The bot restarts "Shape of You" and sends a message like "Got it, I will immediately restart this song".

		Parameters:
			ctx (commands.Context): The context of the command invocation.

		Returns:
			None
		"""
		if not BotState.is_in_use():
			await BotState.log_and_send(ctx, "I am currently not playing any songs")
		else:
			await BotState.log_and_send(
				ctx, "Got it, I will immediately restart this song"
			)
			await self.insert_song(ctx, 1, BotState.current_song_playing)
			await self.next(ctx)

	@commands.command(name="volume", help="Adjust the playback volume (0-100)")
	async def volume(self, ctx):
		"""
		What:
			The `/volume` command prompts the user to provide a volume level between 0 and 100 to adjust the playback volume.

		Why:
			Allowing users to adjust the volume ensures that the audio levels are comfortable and suitable for their listening environment, enhancing the overall experience.

		How:
			- Sends a message requesting the user to provide a valid volume level.
			- Waits for the user's response and adjusts the volume accordingly.

		Example:
			A user types `/volume` without specifying a level. The bot responds with "Please provide a volume between 0 and 100."

		Parameters:
			ctx (commands.Context): The context of the command invocation.

		Returns:
			None
		"""
		await BotState.log_and_send(ctx, "Please provide a volume between 0 and 100.")

	@commands.command(name="volume", help="Adjust the playback volume (0-100)")
	async def volume(self, ctx, volume: int = -1):
		"""
		What:
			The `/volume` command adjusts the playback volume to the specified level between 0 and 100.

		Why:
			Providing precise volume control allows users to tailor the audio output to their preferences and environmental needs, ensuring a pleasant listening experience.

		How:
			- Validates the provided volume level to ensure it is within the acceptable range (0-100).
			- Normalizes the volume level for internal use.
			- Updates the bot's volume setting.
			- Sends confirmation messages to inform users of the volume change.

		Example:
			A user types `/volume 75`. The bot sets the playback volume to 75% and sends a message like "Volume changed from 50% to 75%".

		Parameters:
			ctx (commands.Context): The context of the command invocation.
			volume (int, optional): The desired volume level (0-100). Defaults to -1 if not provided.

		Returns:
			None
		"""
		if 0 <= volume <= 100:
			normalized_volume = volume / 100
			oldvolume = int(BotState.get_volume() * 100)
			BotState.set_volume(ctx.guild.voice_client, normalized_volume)
			await BotState.log_and_send(ctx, f"Volume changed from {oldvolume}% to {volume}%")
		else:
			await BotState.log_and_send(ctx, "Please provide a volume between 0 and 100.")

	@staticmethod
	async def setup(client):
		"""
		What:
			The `setup` static method registers the `SongQueueCog` with the provided Discord client.

		Why:
			Registering the cog ensures that all defined commands and functionalities are recognized and handled by the bot, making them available for user interactions.

		How:
			- Adds an instance of `SongQueueCog` to the Discord client.

		Example:
			```python
			bot = commands.Bot(command_prefix="/")
			await SongQueueCog.setup(bot)
			```

		Parameters:
			client (discord.Client): The Discord client instance to which the cog will be added.

		Returns:
			None
		"""
		await client.add_cog(SongQueueCog(client))
