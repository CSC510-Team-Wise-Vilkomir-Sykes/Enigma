"""
bot_state.py

This module defines the `BotState` class, which manages the shared state of the Discord bot's music playback,
including the song queue, playback status, and logging.

**Attributes**:
- `song_queue` (list): A queue of songs selected by the user.
- `current_song_playing` (Song): The currently playing song.
- `_is_paused` (bool): Indicates whether playback is paused.
- `_is_looping` (bool): Indicates whether looping mode is enabled.
- `logger` (logging.Logger): Logger instance for tracking bot commands and actions.
- `volume` (float): Playback volume (default: 50%).

**Why**:
Centralizes the bot's state and playback control, making it easy to manage music-related operations and
log actions consistently.

**How**:
- Use class-level methods to interact with shared attributes and perform actions like pause, unpause, stop, and volume control.
- Log user interactions with commands and playback.
"""

class BotState:
	"""
	Manages the shared state and playback control of the Discord bot.

	**Why**: Provides centralized control over the bot's music operations, ensuring consistent state management
	and logging across commands and events.

	**How**:
	- Use methods like `pause`, `unpause`, and `stop` to manage playback.
	- Adjust settings such as volume or looping mode using class-level attributes and methods.
	"""

	song_queue = []  # Queue of songs selected by the user
	current_song_playing = None  # Currently playing song, if any
	_is_paused = False  # Indicates if playback is paused
	_is_looping = False  # Indicates if looping is enabled for the current song
	logger = None  # Logger for tracking bot commands and actions
	volume = 0.5  # Default volume (50%)

	@classmethod
	def log_command(cls, ctx, msg):
		"""
		Logs a command action with the specified message.

		:param ctx: The context of the command, used to access author and command name.
		:type ctx: Context
		:param msg: The message to log, providing additional details.
		:type msg: str

		**Why**: Keeps track of user commands and their outcomes for debugging and auditing purposes.
		"""
		cls.logger.info(f"ENIGMA ({ctx.author.name} /{ctx.command.name}) {msg}")

	@classmethod
	async def log_and_send(cls, ctx, msg):
		"""
		Sends a message to the user and logs the command action.

		:param ctx: The context of the command, used for logging and sending messages.
		:type ctx: Context
		:param msg: The message to send and log.
		:type msg: str

		**Why**: Ensures consistent communication with users while maintaining logs for actions taken.
		"""
		await ctx.send(msg)  # Send message to the Discord channel
		cls.log_command(ctx, msg)  # Log the command action

	@classmethod
	def is_in_use(cls):
		"""
		Checks if a song is currently playing.

		:return: True if a song is playing, False otherwise.
		:rtype: bool

		**Why**: Determines whether the bot is active in playing music.
		"""
		return cls.current_song_playing is not None

	@classmethod
	def is_paused(cls):
		"""
		Checks if playback is paused.

		:return: True if playback is paused, False otherwise.
		:rtype: bool

		**Why**: Provides the bot's current playback state for decision-making in commands.
		"""
		return cls._is_paused

	@classmethod
	def is_in_voice_channel(cls, voice_client):
		"""
		Checks if the bot is connected to a voice channel.

		:param voice_client: The Discord voice client instance.
		:type voice_client: VoiceClient
		:return: True if the bot is connected to a voice channel, False otherwise.
		:rtype: bool

		**Why**: Ensures that playback operations only occur when the bot is in a valid voice channel.
		"""
		return voice_client is not None and voice_client.is_connected()

	@classmethod
	def pause(cls, voice_client):
		"""
		Pauses playback if a song is currently playing and the bot is connected to a voice channel.

		:param voice_client: The Discord voice client instance.
		:type voice_client: VoiceClient

		**Why**: Temporarily halts music playback without clearing the queue or playback state.
		"""
		if not cls._is_paused and cls.is_in_use():
			if voice_client is not None and not voice_client.is_paused():
				voice_client.pause()  # Pause playback on the voice client
			cls._is_paused = True  # Update the pause state

	@classmethod
	def unpause(cls, voice_client):
		"""
		Resumes playback if paused and the bot is connected to a voice channel.

		:param voice_client: The Discord voice client instance.
		:type voice_client: VoiceClient

		**Why**: Restarts playback after a pause, maintaining the playback state.
		"""
		if cls._is_paused and cls.is_in_use():
			if voice_client is not None and voice_client.is_paused():
				voice_client.resume()  # Resume playback on the voice client
			cls._is_paused = False  # Update the pause state

	@classmethod
	def stop(cls, voice_client):
		"""
		Stops playback and resets playback-related attributes.

		:param voice_client: The Discord voice client instance.
		:type voice_client: VoiceClient

		**Why**: Ends playback and clears the current state when the bot leaves or stops music.
		"""
		if voice_client is not None and cls.is_in_use():
			voice_client.stop()  # Stop playback on the voice client
		cls.current_song_playing = None  # Reset the current song
		cls._is_paused = False  # Reset the pause state

	@classmethod
	def is_looping(cls):
		"""
		Checks if the bot is in looping mode.

		:return: True if looping is enabled, False otherwise.
		:rtype: bool

		**Why**: Identifies if the current song will be replayed after finishing.
		"""
		return cls._is_looping

	@classmethod
	def set_is_looping(cls, is_looping):
		"""
		Sets the looping state of the bot.

		:param is_looping: The new looping state to set.
		:type is_looping: bool

		**Why**: Toggles looping mode for the currently playing song.
		"""
		cls._is_looping = is_looping  # Update the looping state

	@classmethod
	def set_volume(cls, voice_client, volume):
		"""
		Sets the playback volume.

		:param voice_client: The Discord voice client instance.
		:type voice_client: VoiceClient
		:param volume: The new volume level (0.0 to 1.0).
		:type volume: float

		**Why**: Provides volume control for playback, ensuring user preferences are met.
		"""
		if 0.0 <= volume <= 1.0:
			cls.volume = volume
			if voice_client and voice_client.source:
				voice_client.source.volume = volume
			cls.logger.info(f"Volume set to {volume * 100}%")
		else:
			cls.logger.warning(f"Attempted to set invalid volume: {volume}")

	@classmethod
	def get_volume(cls):
		"""
		Gets the current playback volume.

		:return: The current volume level (0.0 to 1.0).
		:rtype: float

		**Why**: Allows users to view the current volume level for playback.
		"""
		return cls.volume
