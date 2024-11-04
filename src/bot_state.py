"""
bot_state.py

This module defines the BotState class, which manages the shared state of the Discord bot's music playback, including
the song queue, playback status, and logging.

Attributes:
    - song_queue (list): A queue of songs selected by the user.
    - current_song_playing (Song): The currently playing song.
    - _is_paused (bool): Indicates whether the bot is currently paused.
    - _is_looping (bool): Indicates whether the bot is in looping mode.
    - logger (logging.Logger): Logger instance for tracking bot commands and actions.
"""

class BotState:
    song_queue = []  # Queue of songs selected by the user
    current_song_playing = None  # Currently playing song, if any
    _is_paused = False  # Indicates if playback is paused
    _is_looping = False  # Indicates if looping is enabled for the current song
    logger = None  # Logger for tracking bot commands and actions

    @classmethod
    def log_command(cls, ctx, msg):
        """Logs a command action with the specified message.

            Args:
                ctx (Context): The context of the command, used to access author and command name.
                msg (str): The message to log, providing additional details.
        """
        cls.logger.info(f"ENIGMA ({ctx.author.name} /{ctx.command.name}) {msg}")

    @classmethod
    async def log_and_send(cls, ctx, msg):
        """Sends a message to the user and logs the command action.

            Args:
                ctx (Context): The context of the command, used for logging and sending messages.
                msg (str): The message to send and log.
        """
        await ctx.send(msg)  # Send message to the Discord channel
        cls.log_command(ctx, msg)  # Log the command action

    @classmethod
    def is_in_use(cls):
        """Checks if a song is currently playing.

            Returns:
                bool: True if a song is playing, False otherwise.
        """
        return cls.current_song_playing is not None

    @classmethod
    def is_paused(cls):
        """Checks if playback is paused.

            Returns:
                bool: True if playback is paused, False otherwise.
        """
        return cls._is_paused

    @classmethod
    def is_in_voice_channel(cls, voice_client):
        """Checks if the bot is connected to a voice channel.

            Args:
                voice_client (VoiceClient): The Discord voice client instance.

            Returns:
                bool: True if the bot is connected to a voice channel, False otherwise.
        """
        return voice_client is not None and voice_client.is_connected()

    @classmethod
    def pause(cls, voice_client):
        """Pauses playback if a song is currently playing and the bot is connected to a voice channel.

            Args:
                voice_client (VoiceClient): The Discord voice client instance.
        """
        if not cls._is_paused and cls.is_in_use():
            if voice_client is not None and not voice_client.is_paused():
                voice_client.pause()  # Pause playback on the voice client
            cls._is_paused = True  # Update the pause state

    @classmethod
    def unpause(cls, voice_client):
        """Resumes playback if paused and the bot is connected to a voice channel.

            Args:
                voice_client (VoiceClient): The Discord voice client instance.
        """
        if cls._is_paused and cls.is_in_use():
            if voice_client is not None and voice_client.is_paused():
                voice_client.resume()  # Resume playback on the voice client
            cls._is_paused = False  # Update the pause state

    @classmethod
    def stop(cls, voice_client):
        """Stops playback and resets playback-related attributes.

            Args:
                voice_client (VoiceClient): The Discord voice client instance.
        """
        if voice_client is not None and cls.is_in_use():
            voice_client.stop()  # Stop playback on the voice client
        cls.current_song_playing = None  # Reset the current song
        cls._is_paused = False  # Reset the pause state

    @classmethod
    def is_looping(cls):
        """Checks if the bot is in looping mode.

            Returns:
                bool: True if looping is enabled, False otherwise.
        """
        return cls._is_looping

    @classmethod
    def set_is_looping(cls, is_looping):
        """Sets the looping state of the bot.

            Args:
                is_looping (bool): The new looping state to set.
        """
        cls._is_looping = is_looping  # Update the looping state
