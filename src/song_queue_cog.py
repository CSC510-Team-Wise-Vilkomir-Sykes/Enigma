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
import youtube_dl

FFMPEG_OPTIONS = {
    'before_options':
    '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': [
        'ffmpeg', '-i', './assets/sample.mp4', '-vn', '-f', 'mp3',
        './assets/sample.mp3'
    ]
}
YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist': 'True'}


class SongQueueCog(commands.Cog):
    """
    Cog for bot that handles all commands related to song queues
    """

    def __init__(self, bot):
        self.bot = bot

    """
    Function for handling resume capability
    """

    @commands.command(name='resume', help='Resumes the song')
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
        else:
            await ctx.send(
                "The bot was not playing anything before this. Use play command"
            )

    """
    Function for playing a custom song
    """

    @commands.command(name='play_custom', help='To play custom song')
    async def play_custom(self, ctx):
        user_message = str(ctx.message.content)
        song_name = user_message.split(' ', 1)[1]
        await self.play_song(song_name, ctx)

    """
    Function to stop playing the music
    """

    @commands.command(name='stop', help='Stops the song')
    async def stop(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    """
    Helper function for playing song on the voice channel
    """

    async def play_song(self, song_name, ctx):
        # First stop whatever the bot is playing
        await self.stop(ctx)
        try:
            server = ctx.message.guild
            voice_channel = server.voice_client
            url = searchSong(song_name)
            async with ctx.typing():
                with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(url, download=False)
                    I_URL = info['formats'][0]['url']
                    source = await discord.FFmpegOpusAudio.from_probe(
                        I_URL, **FFMPEG_OPTIONS)
                    voice_channel.play(source)
                    voice_channel.is_playing()
            await ctx.send('**Now playing:** {}'.format(song_name))
        except Exception as e:
            await ctx.send("The bot is not connected to a voice channel.")

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
