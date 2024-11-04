"""
This file is responsible for all bot commands regarding songs such /poll for generating recommendations,
/next_song for playing next song and so on
"""

import asyncio

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
    Cog for bot that handles all commands related to song queues and song playback
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="join", help="Joins the voice channel of the user")
    async def join(self, ctx):
        """
        /join will make the bot join/switch to the voice channel the user is in

        :param ctx: the command context
        """
        # Check if the user is in a voice channel
        if ctx.author.voice and ctx.author.voice.channel:
            user_channel = ctx.author.voice.channel
            voice_client = ctx.guild.voice_client

            # Check if the bot is already in a voice channel
            if BotState.is_in_voice_channel(voice_client):
                if voice_client.channel == user_channel:
                    await BotState.log_and_send(
                        ctx, f"I am already in this voice channel ({user_channel.name})"
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
        /leave will force the bot to leave its current voice channel

        :param ctx: the command context
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

    """
        Function to stop playing the music
    """

    @commands.command(name="pause", help="Pauses the song")
    async def pause(self, ctx):
        """
        /pause will pause the currently playing music

        :param ctx: the command context
        :return:
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
                await BotState.log_and_send(ctx, "I am currently not playing anything")
        else:
            await BotState.log_and_send(
                ctx, "I am currently not connected to a voice channel"
            )

    """
    Function for handling resume capability
    """

    @commands.command(name="unpause", help="unpauses the song")
    async def unpause(self, ctx):
        """
        /unpause will unpause the currently playing music

        :param ctx: the command context
        :return:
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
                await BotState.log_and_send(ctx, "I am currently not playing anything")
        else:
            await BotState.log_and_send(
                ctx, "I am currently not connected to a voice channel"
            )

    """
    Function for playing a custom song
    """

    @commands.command(name="queue", help="queue a custom song")
    async def queue(self, ctx, *, query):
        """
        /queue will add a song query to the end of the queue

        :param ctx: the command context
        :param query: the query (song) to queue
        """
        song = await self.ensure_song(ctx, query)
        if song is not None:
            # remember that commands expect queue idx to start at 1
            if await self.insert_song(ctx, len(BotState.song_queue) + 1, song):
                await BotState.log_and_send(ctx, f"Queued song: {song}")

    @commands.command(name="insert", help="insert a custom song")
    async def insert(self, ctx, *, params):
        """
        /insert will insert a song query into an arbitrary point in the queue

        :param ctx: the command context
        :param params: the index and song query, separated by a space
        """
        idx, query = params.split(" ", maxsplit=1)
        song = await self.ensure_song(ctx, query)
        if song is not None:
            if await self.insert_song(ctx, idx, song):
                await BotState.log_and_send(
                    ctx, f"Inserted song {song} as track number {idx}"
                )

    @commands.command(name="insertfront", help="insert a custom song at the front")
    async def insertfront(self, ctx, *, query):
        """
        /insertfront will insert a song into the front of the queue

        :param ctx: the command context
        :param query: the song to insert
        """
        # remember that commands expect queue idx to start at 1
        await self.insert(ctx, params=f"1 {query}")

    @staticmethod
    async def insert_song(ctx, idx, song):
        """
        helper function to insert songs into the queue

        :param ctx: the command context
        :param idx: the index to add it to
        :param song: the song object
        """
        idx = await SongQueueCog.ensure_insert_number(ctx, idx)
        if idx is not None:
            BotState.song_queue.insert(idx, song)
            return True
        return False

    @staticmethod
    async def delete_track(ctx, idx):
        """
        helper function to delete songs in the queue

        :param ctx: the command context
        :param idx: the index to remove
        """
        idx = await SongQueueCog.ensure_track_number(ctx, idx)
        if idx is not None:
            removed_song = BotState.song_queue.pop(idx)
            return removed_song
        return None

    @staticmethod
    async def ensure_song(ctx, query):
        """
        helper function to convert a query into a song object

        :param ctx: the command context
        :param query: query string to convert
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
        helper function to ensure a valid track number, then convert it from a list-start-at-1 idx to a list-start-at-0 idx

        :param ctx: the command context
        :param idx: the index
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
        helper function to ensure a valid insertion number, then convert it from a list-start-at-1 idx to a list-start-at-0 idx

        :param ctx: the command context
        :param idx: the index
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
        helper function for playing a song

        :param ctx: the command context
        :param idx: the song object to play
        """
        voice_client = ctx.message.guild.voice_client
        if voice_client:
            # Search for the song on YouTube
            info = ytdl.extract_info(f"ytsearch:{song}", download=False)["entries"][0]
            url = info["url"]

            if BotState.is_in_use():
                BotState.stop(voice_client)
                BotState.log_command(
                    ctx, f"Terminating current song {BotState.current_song_playing}"
                )

            while BotState.is_in_use():
                # we must wait for the previous song to clean up
                pass

            # Play the audio stream
            ctx.voice_client.play(
                discord.FFmpegPCMAudio(url, **ffmpeg_options),
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
        function that runs once a song is terminated or ends normally, will typically play the next song
        if one is available

        :param ctx: the command context
        :param error: any error that was thrown during playback
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
        /next will play the next song in the queue if one exists

        :param ctx: the command context
        """
        if BotState.is_in_use():
            BotState.stop(ctx.guild.voice_client)
        else:
            await self.play_next_song(ctx)

    async def play_next_song(self, ctx):
        """
        helper function to play the next song if one exists

        :param ctx: the command context
        """
        if len(BotState.song_queue) == 0:
            await BotState.log_and_send(ctx, f"Please add a song to the queue first")
        else:
            next_song = BotState.song_queue.pop(0)
            await self.play_song(ctx, next_song)
    @commands.command(name="view", help="Show current queue and currently playing song")
    async def view(self, ctx):
        """
        /view will show the current queue and currently playing song

        :param ctx: the command context
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

    @commands.command(name="shuffle", help="To shuffle songs in queue")
    async def shuffle(self, ctx):
        """
        /shuffle will shuffle all the songs in the queue

        :param ctx: the command context
        """
        if len(BotState.song_queue) == 0:
            await ctx.send(f"No songs in queue. Try /queue <query> to get started")
        else:
            random.shuffle(BotState.song_queue)
            await ctx.send(f"Shuffled! Do /view to see the current queue")

        BotState.log_command(ctx, "Acknowledged")

    @commands.command(name="jumpto", help="Jump to a track number")
    async def jumpto(self, ctx, *, idx):
        """
        /jumpto will jump to the provided track

        :param ctx: the command context
        :param idx: the track index to jump to
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
        help="Move the song at the given track number in a different position in the queue",
    )
    async def move(self, ctx, *, params):
        """
        /move will move a song at one track number to be at a different track number

        :param ctx: the command context
        :param params: the two indices to swap
        """
        src_idx, dest_idx = params.split(" ", maxsplit=1)

        # dest_idx is ensured as a track number (0 < idx < size) and not as an insertion number (0 < idx <= size)
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
                        f"Moved {moved_song} from track {src_idx} to track {dest_idx}",
                    )

    @commands.command(
        name="remove", help="Removes the song in the queue at the given track number"
    )
    async def remove(self, ctx, *, idx):
        """
        /remove will remove the song at the given track number

        :param ctx: the command context
        :param idx: the track index to remove
        """
        removed_song = await self.delete_track(ctx, idx)
        if removed_song is not None:
            await BotState.log_and_send(
                ctx, f"Removed {removed_song} (track number {idx})"
            )

    @commands.command(name="movefront", help="Moves a song to the front of the queue")
    async def movefront(self, ctx, *, src_idx):
        """
        /movefront will move a song to the front of the queue

        :param ctx: the command context
        :param idx: the track index to remove
        """
        # remember that commands expect queue idx to start at 1
        await self.move(ctx, params=f"{src_idx} 1")

    @commands.command(name="moveback", help="Moves a song to the back of the queue")
    async def moveback(self, ctx, *, src_idx):
        """
        /moveback will move a song to the back of the queue

        :param ctx: the command context
        :param idx: the track index to remove
        """
        # remember that commands expect queue idx to start at 1
        await self.move(ctx, params=f"{src_idx} {len(BotState.song_queue)}")

    @commands.command(
        name="replay", help="Will replay the currently playing song once after it ends"
    )
    async def replay(self, ctx):
        """
        /replay will replay the currently playing song once it's done

        :param ctx: the command context
        """
        if not BotState.is_in_use():
            await BotState.log_and_send(ctx, "I am currently not playing any songs")
        else:
            if BotState.is_looping():
                await BotState.log_and_send(ctx, "I am already set to loop")
            else:
                await self.insert_song(ctx, 1, BotState.current_song_playing)
                await BotState.log_and_send(
                    ctx, "Got it, I will add this song to the front of the queue again"
                )

    @commands.command(
        name="replaynow", help="Will immediately restart the currently playing song"
    )
    async def replaynow(self, ctx):
        """
        /replay will replay the currently playing song immediately

        :param ctx: the command context
        """
        if not BotState.is_in_use():
            await BotState.log_and_send(ctx, "I am currently not playing any songs")
        else:
            await BotState.log_and_send(
                ctx, "Got it, I will immediately restart this song"
            )
            await self.insert_song(ctx, 1, BotState.current_song_playing)
            await self.next(ctx)

    @staticmethod
    async def setup(client):
        """
        Helper function to register this cog into the client

        :param client: the client to register this cog for
        """
        await client.add_cog(SongQueueCog(client))
