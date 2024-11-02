class BotState:
    song_queue = []
    current_song_playing = None
    _is_paused = False
    _is_in_voice_channel = False
    _is_looping = False
    logger = None

    @classmethod
    def log_command(cls, ctx, msg):
        cls.logger.info(f"ENIGMA ({ctx.author.name} /{ctx.command.name}) {msg}")

    @classmethod
    async def log_and_send(cls, ctx, msg):
        await ctx.send(msg)
        cls.log_command(ctx, msg)

    @classmethod
    def is_in_use(cls):
        return cls.current_song_playing is not None

    @classmethod
    def is_paused(cls):
        return cls._is_paused

    @classmethod
    def is_in_voice_channel(cls):
        return cls._is_in_voice_channel

    @classmethod
    def set_is_in_voice_channel(cls, is_in_voice_channel, voice_client):
        if is_in_voice_channel != cls._is_in_voice_channel:
            cls._is_in_voice_channel = is_in_voice_channel
            cls.stop(voice_client)

    @classmethod
    def pause(cls, voice_client):
        if not cls._is_paused and cls.is_in_use():
            if not voice_client.is_paused():
                voice_client.pause()
            cls._is_paused = True

    @classmethod
    def unpause(cls, voice_client):
        if cls._is_paused and cls.is_in_use():
            if voice_client.is_paused():
                voice_client.resume()
            cls._is_paused = False

    @classmethod
    def stop(cls, voice_client):
        if cls.is_in_use():
            if voice_client.is_playing():
                voice_client.stop()
            cls.current_song_playing = None
        cls._is_paused = False

    @classmethod
    def is_looping(cls):
        return cls._is_looping

    @classmethod
    def set_is_looping(cls, is_looping):
        cls._is_looping = is_looping
