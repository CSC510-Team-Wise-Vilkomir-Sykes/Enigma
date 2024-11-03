import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import discord

from src.bot_state import BotState
from src.song_queue_cog import SongQueueCog
from discord.ext import commands


class TestSongQueueCog(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Create an actual bot instance for testing
        intents = discord.Intents.all()
        self.bot = commands.Bot(command_prefix="/", intents=intents)
        self.cog = SongQueueCog(self.bot)  # Initialize the cog
        await self.bot.add_cog(
            self.cog
        )  # Ensure the cog is added to the bot for command registration

    @patch("src.bot_state.BotState.is_in_voice_channel", return_value=False)
    @patch("src.bot_state.BotState.log_and_send", new_callable=AsyncMock)
    async def test_join_user_not_in_channel(
        self, mock_log_and_send, mock_is_in_voice_channel
    ):
        # Mock ctx with user not in a voice channel
        mock_ctx = AsyncMock()
        mock_ctx.author.voice = None  # User is not in a voice channel

        await self.cog.join(mock_ctx)

        # Ensure log_and_send was called with the expected message
        mock_log_and_send.assert_called_once_with(
            mock_ctx, "Please join a voice channel before executing /join"
        )

    @patch("src.bot_state.BotState.is_in_voice_channel", return_value=True)
    @patch("src.bot_state.BotState.log_and_send", new_callable=AsyncMock)
    async def test_join_user_already_in_channel(
        self, mock_log_and_send, mock_is_in_voice_channel
    ):
        # Mock ctx with user in the same voice channel
        mock_ctx = AsyncMock()
        mock_channel = AsyncMock()
        mock_channel.name = "Test Channel"
        mock_ctx.author.voice.channel = mock_channel
        mock_ctx.guild.voice_client.channel = (
            mock_channel  # Bot is already in the same channel
        )

        await self.cog.join(mock_ctx)

        # Ensure log_and_send was called indicating the bot is already in the channel
        mock_log_and_send.assert_called_once_with(
            mock_ctx, f"I am already in this voice channel ({mock_channel.name})"
        )

    @patch("src.bot_state.BotState.is_in_voice_channel", return_value=True)
    @patch("src.bot_state.BotState.log_and_send", new_callable=AsyncMock)
    async def test_join_user_switch_channel(
        self, mock_log_and_send, mock_is_in_voice_channel
    ):
        # Mock ctx with user in a different voice channel
        mock_ctx = AsyncMock()
        mock_user_channel = AsyncMock()
        mock_user_channel.name = "User Channel"
        mock_ctx.author.voice.channel = mock_user_channel

        mock_voice_client = AsyncMock()
        mock_ctx.guild.voice_client = mock_voice_client
        mock_voice_client.channel = AsyncMock()  # Simulate current channel
        mock_voice_client.channel.name = "Current Channel"

        # Invoke the join command
        await self.cog.join(mock_ctx)

        # Ensure the bot switches to the new channel
        mock_voice_client.move_to.assert_awaited_once_with(mock_user_channel)

        # Ensure log_and_send was called with the expected switch message
        mock_log_and_send.assert_called_once_with(
            mock_ctx, f"Switched to voice channel: {mock_user_channel.name}"
        )

    @patch("src.bot_state.BotState.is_in_voice_channel", return_value=False)
    @patch("src.bot_state.BotState.log_and_send", new_callable=AsyncMock)
    async def test_join_user_channel(self, mock_log_and_send, mock_is_in_voice_channel):
        # Mock ctx with user in a voice channel
        mock_ctx = AsyncMock()
        mock_user_channel = AsyncMock()
        mock_user_channel.name = "User Channel"
        mock_ctx.author.voice.channel = mock_user_channel  # User is in a channel

        # Mock the connect method on the user channel
        mock_user_channel.connect = AsyncMock()

        # Invoke the join command
        await self.cog.join(mock_ctx)

        # Ensure the bot joins the user's voice channel
        mock_user_channel.connect.assert_awaited_once()

        # Ensure log_and_send was called with the expected join message
        mock_log_and_send.assert_called_once_with(
            mock_ctx, f"Joined voice channel: {mock_user_channel.name}"
        )

    @patch("src.bot_state.BotState.is_in_voice_channel", return_value=True)
    @patch("src.bot_state.BotState.log_and_send", new_callable=AsyncMock)
    async def test_leave_success(self, mock_log_and_send, mock_is_in_voice_channel):
        # Mock ctx with bot connected to a voice channel
        mock_ctx = AsyncMock()
        mock_voice_channel = AsyncMock()  # Mock the voice channel
        mock_voice_channel.name = "Test Channel"  # Set a name for the voice channel
        mock_ctx.guild.voice_client = AsyncMock()  # Mock the voice client
        mock_ctx.guild.voice_client.channel = (
            mock_voice_channel  # Set the channel for the voice client
        )

        # Invoke the leave command as Discord would
        command = self.bot.get_command("leave")
        await command.invoke(mock_ctx)

        # Ensure the voice client disconnect method was called
        mock_ctx.guild.voice_client.disconnect.assert_awaited_once()

        # Ensure log_and_send was called with the expected message
        mock_log_and_send.assert_called_once_with(
            mock_ctx, "Left voice channel: Test Channel"
        )

    @patch("src.bot_state.BotState.is_in_voice_channel", return_value=False)
    @patch("src.bot_state.BotState.log_and_send", new_callable=AsyncMock)
    async def test_leave_not_connected(
        self, mock_log_and_send, mock_is_in_voice_channel
    ):
        # Mock ctx with bot not connected to a voice channel
        mock_ctx = AsyncMock()
        mock_ctx.guild.voice_client = None  # Not in a voice channel

        # Retrieve the leave command from the bot
        command = self.bot.get_command("leave")

        # Ensure the command is an actual command
        self.assertIsNotNone(
            command, "Command 'leave' should be registered in the bot."
        )

        # Invoke the command as Discord would
        await command.invoke(mock_ctx)

        # Ensure log_and_send was called with the expected message
        mock_log_and_send.assert_called_once_with(
            mock_ctx, "I am currently not connected to a voice channel"
        )

    @patch("src.bot_state.BotState.is_in_use", return_value=False)
    @patch("src.bot_state.BotState.log_and_send", new_callable=AsyncMock)
    async def test_pause_not_playing(self, mock_log_and_send, mock_is_in_use):
        # Mock ctx with bot connected to a voice channel
        mock_ctx = AsyncMock()
        mock_ctx.message.guild.voice_client = AsyncMock()  # Bot is connected

        await self.cog.pause(mock_ctx)

        # Ensure log_and_send was called indicating nothing is playing
        mock_log_and_send.assert_called_once_with(
            mock_ctx, "I am currently not playing anything"
        )

    @patch("src.bot_state.BotState.is_in_use", return_value=True)
    @patch("src.bot_state.BotState.is_paused", return_value=True)
    @patch("src.bot_state.BotState.log_and_send", new_callable=AsyncMock)
    async def test_pause_already_paused(
        self, mock_log_and_send, mock_is_paused, mock_is_in_use
    ):
        # Mock ctx with bot connected and already paused
        mock_ctx = AsyncMock()
        mock_ctx.message.guild.voice_client = AsyncMock()

        await self.cog.pause(mock_ctx)

        # Ensure log_and_send was called indicating already paused
        mock_log_and_send.assert_called_once_with(mock_ctx, "I am already paused")

    @patch("src.bot_state.BotState.is_in_use", return_value=True)
    @patch("src.bot_state.BotState.is_paused", return_value=False)
    @patch("src.bot_state.BotState.pause", new_callable=AsyncMock)
    @patch("src.bot_state.BotState.log_and_send", new_callable=AsyncMock)
    async def test_pause_success(
        self, mock_log_and_send, mock_pause, mock_is_paused, mock_is_in_use
    ):
        # Mock ctx with bot connected and not paused
        mock_ctx = AsyncMock()
        mock_ctx.message.guild.voice_client = AsyncMock()

        await self.cog.pause(mock_ctx)

        # Ensure the bot pauses the music and sends the expected message
        mock_pause.assert_called_once_with(mock_ctx.message.guild.voice_client)
        mock_log_and_send.assert_called_once_with(mock_ctx, "Pausing music")

    @patch("src.bot_state.BotState.is_in_use", return_value=False)
    @patch("src.bot_state.BotState.log_and_send", new_callable=AsyncMock)
    async def test_unpause_not_playing(self, mock_log_and_send, mock_is_in_use):
        # Mock ctx with bot connected to a voice channel
        mock_ctx = AsyncMock()
        mock_ctx.message.guild.voice_client = AsyncMock()

        await self.cog.unpause(mock_ctx)

        # Ensure log_and_send was called indicating nothing is playing
        mock_log_and_send.assert_called_once_with(
            mock_ctx, "I am currently not playing anything"
        )

    @patch("src.bot_state.BotState.is_in_use", return_value=True)
    @patch("src.bot_state.BotState.is_paused", return_value=False)
    @patch("src.bot_state.BotState.log_and_send", new_callable=AsyncMock)
    async def test_unpause_already_unpaused(
        self, mock_log_and_send, mock_is_paused, mock_is_in_use
    ):
        # Mock ctx with bot connected and already unpaused
        mock_ctx = AsyncMock()
        mock_ctx.message.guild.voice_client = AsyncMock()

        await self.cog.unpause(mock_ctx)

        # Ensure log_and_send was called indicating already unpaused
        mock_log_and_send.assert_called_once_with(mock_ctx, "I am already unpaused")

    @patch("src.bot_state.BotState.is_in_use", return_value=True)
    @patch("src.bot_state.BotState.is_paused", return_value=True)
    @patch("src.bot_state.BotState.unpause", new_callable=AsyncMock)
    @patch("src.bot_state.BotState.log_and_send", new_callable=AsyncMock)
    async def test_unpause_success(
        self, mock_log_and_send, mock_unpause, mock_is_paused, mock_is_in_use
    ):
        # Mock ctx with bot connected and paused
        mock_ctx = AsyncMock()
        mock_ctx.message.guild.voice_client = AsyncMock()

        await self.cog.unpause(mock_ctx)

        # Ensure the bot unpauses the music and sends the expected message
        mock_unpause.assert_called_once_with(mock_ctx.message.guild.voice_client)
        mock_log_and_send.assert_called_once_with(mock_ctx, "Unpausing music")

    @patch("src.bot_state.BotState.song_queue", new_callable=list)
    @patch("src.song_queue_cog.SongQueueCog.ensure_song", return_value="Test Song")
    @patch("src.song_queue_cog.SongQueueCog.insert_song", return_value=True)
    @patch("src.bot_state.BotState.log_and_send", new_callable=AsyncMock)
    async def test_insert_success(
        self, mock_log_and_send, mock_insert_song, mock_ensure_song, mock_song_queue
    ):
        # Mock ctx
        mock_ctx = AsyncMock()

        await self.cog.insert(mock_ctx, params="1 Test Song")

        # Ensure the song was inserted and the log message was sent
        mock_insert_song.assert_called_once_with(mock_ctx, "1", "Test Song")
        mock_log_and_send.assert_called_once_with(
            mock_ctx, "Inserted song Test Song as track number 1"
        )

    @patch("src.bot_state.BotState.song_queue", new_callable=list)
    @patch("src.song_queue_cog.SongQueueCog.ensure_song", return_value="Test Song")
    @patch("src.song_queue_cog.SongQueueCog.insert_song", return_value=False)
    @patch("src.bot_state.BotState.log_and_send", new_callable=AsyncMock)
    async def test_insert_failure(
        self, mock_log_and_send, mock_insert_song, mock_ensure_song, mock_song_queue
    ):
        # Mock ctx
        mock_ctx = AsyncMock()

        await self.cog.insert(mock_ctx, params="1 Test Song")

        # Ensure the song was not inserted and no log message was sent
        mock_insert_song.assert_called_once_with(mock_ctx, "1", "Test Song")
        mock_log_and_send.assert_not_called()

    @patch("src.bot_state.BotState.song_queue", new_callable=list)
    @patch("src.song_queue_cog.SongQueueCog.ensure_song", return_value="Test Song")
    @patch("src.song_queue_cog.SongQueueCog.insert_song", return_value=True)
    @patch("src.bot_state.BotState.log_and_send", new_callable=AsyncMock)
    async def test_insertfront_success(
        self, mock_log_and_send, mock_insert_song, mock_ensure_song, mock_song_queue
    ):
        # Mock ctx
        mock_ctx = AsyncMock()

        await self.cog.insertfront(mock_ctx, query="Test Song")

        # Ensure the song was inserted at the front and the log message was sent
        mock_insert_song.assert_called_once_with(mock_ctx, "1", "Test Song")
        mock_log_and_send.assert_called_once_with(
            mock_ctx, "Inserted song Test Song as track number 1"
        )

    @patch("src.bot_state.BotState.is_in_use", return_value=True)
    @patch("src.bot_state.BotState.stop")
    async def test_next_when_in_use(self, mock_stop, mock_is_in_use):
        # Mock ctx
        mock_ctx = AsyncMock()

        # Invoke the command
        await self.cog.next(mock_ctx)

        # Ensure the stop method was called
        mock_stop.assert_called_once_with(mock_ctx.guild.voice_client)

    @patch("src.bot_state.BotState.is_in_use", return_value=False)
    @patch("src.song_queue_cog.SongQueueCog.play_next_song", new_callable=AsyncMock)
    async def test_next_when_not_in_use(self, mock_play_next_song, mock_is_in_use):
        # Mock ctx
        mock_ctx = AsyncMock()

        # Invoke the command
        await self.cog.next(mock_ctx)

        # Ensure play_next_song was called
        mock_play_next_song.assert_called_once_with(mock_ctx)

    @patch("src.bot_state.BotState.song_queue", new_callable=list)
    @patch("src.song_queue_cog.SongQueueCog.ensure_track_number", return_value=1)
    @patch("src.bot_state.BotState.log_and_send", new_callable=AsyncMock)
    async def test_jumpto_success(
        self, mock_log_and_send, mock_ensure_track_number, mock_song_queue
    ):
        # Set up mock context and song queue
        mock_ctx = AsyncMock()
        mock_song_queue.extend(
            ["Song 1", "Song 2", "Song 3", "Song 4"]
        )  # Add songs to the queue

        # Invoke the command
        await self.cog.jumpto(mock_ctx, idx="2")  # Jump to track number 2

        # Ensure the song queue is updated correctly
        self.assertEqual(
            BotState.song_queue,
            ["Song 2", "Song 3", "Song 4"],
            "The song queue should start from track 2.",
        )
        mock_log_and_send.assert_called_once_with(
            mock_ctx, "Jumped to track number 2 in the queue"
        )

    @patch("src.song_queue_cog.SongQueueCog.ensure_track_number", return_value=0)
    @patch("src.song_queue_cog.SongQueueCog.delete_track", return_value="Song to move")
    @patch("src.song_queue_cog.SongQueueCog.insert_song", return_value=True)
    @patch("src.bot_state.BotState.log_and_send", new_callable=AsyncMock)
    async def test_move_success(
        self,
        mock_log_and_send,
        mock_insert_song,
        mock_delete_track,
        mock_ensure_track_number,
    ):
        # Mock context
        mock_ctx = AsyncMock()

        # Mocking initial song queue state
        BotState.song_queue = ["Song 1", "Song 2", "Song 3", "Song 4"]

        # Invoke the command
        await self.cog.move(mock_ctx, params="1 3")  # Move from track 1 to track 3

        # Ensure delete_track was called and the song was inserted in the right position
        mock_delete_track.assert_called_once_with(mock_ctx, "1")
        mock_insert_song.assert_called_once_with(mock_ctx, "3", "Song to move")
        mock_log_and_send.assert_called_once_with(
            mock_ctx, "Moved Song to move from track 1 to track 3"
        )

    @patch(
        "src.song_queue_cog.SongQueueCog.delete_track", return_value="Song to remove"
    )
    @patch("src.bot_state.BotState.log_and_send", new_callable=AsyncMock)
    async def test_remove_success(self, mock_log_and_send, mock_delete_track):
        # Mock context
        mock_ctx = AsyncMock()

        # Mocking initial song queue state
        BotState.song_queue = ["Song 1", "Song 2", "Song 3"]

        # Invoke the command
        await self.cog.remove(mock_ctx, idx="2")  # Remove track number 2

        # Ensure delete_track was called and the log message was sent
        mock_delete_track.assert_called_once_with(mock_ctx, "2")
        mock_log_and_send.assert_called_once_with(
            mock_ctx, "Removed Song to remove (track number 2)"
        )

    @patch("src.bot_state.BotState.song_queue", new_callable=list)
    @patch("src.bot_state.BotState.log_and_send", new_callable=AsyncMock)
    async def test_movefront(self, mock_log_and_send, mock_song_queue):
        mock_ctx = AsyncMock()
        mock_song_queue.extend(["Song 1", "Song 2", "Song 3"])  # Initial queue

        await self.cog.movefront(mock_ctx, src_idx="2")  # Move "Song 2" to the front

        # Ensure the queue has been modified correctly
        self.assertEqual(mock_song_queue, ["Song 2", "Song 1", "Song 3"])
        mock_log_and_send.assert_called_once_with(
            mock_ctx, "Moved Song 2 from track 2 to track 1"
        )

    @patch("src.bot_state.BotState.song_queue", new_callable=list)
    @patch("src.bot_state.BotState.log_and_send", new_callable=AsyncMock)
    async def test_moveback(self, mock_log_and_send, mock_song_queue):
        mock_ctx = AsyncMock()
        mock_song_queue.extend(["Song 1", "Song 2", "Song 3"])  # Initial queue

        await self.cog.moveback(mock_ctx, src_idx="1")  # Move "Song 1" to the back

        # Ensure the queue has been modified correctly
        self.assertEqual(mock_song_queue, ["Song 2", "Song 3", "Song 1"])
        mock_log_and_send.assert_called_once_with(
            mock_ctx, "Moved Song 1 from track 1 to track 3"
        )

    @patch("src.bot_state.BotState.is_in_use", return_value=False)
    @patch("src.bot_state.BotState.log_and_send", new_callable=AsyncMock)
    async def test_replay_not_playing(self, mock_log_and_send, mock_is_in_use):
        mock_ctx = AsyncMock()

        await self.cog.replay(mock_ctx)

        # Ensure the log message is correct when not playing
        mock_log_and_send.assert_called_once_with(
            mock_ctx, "I am currently not playing any songs"
        )

    @patch("src.bot_state.BotState.is_in_use", return_value=True)
    @patch("src.bot_state.BotState.is_looping", return_value=False)
    @patch("src.bot_state.BotState.current_song_playing", new_callable=AsyncMock)
    @patch("src.bot_state.BotState.log_and_send", new_callable=AsyncMock)
    @patch("src.song_queue_cog.SongQueueCog.insert_song", new_callable=AsyncMock)
    async def test_replay_success(
        self,
        mock_insert_song,
        mock_log_and_send,
        mock_is_looping,
        mock_is_in_use,
        mock_current_song_playing,
    ):
        mock_ctx = AsyncMock()
        mock_current_song_playing.return_value = "Current Song"

        await self.cog.replay(mock_ctx)

        # Ensure the song was added to the queue and the correct message was sent
        mock_log_and_send.assert_called_once_with(
            mock_ctx, "Got it, I will add this song to the front of the queue again"
        )


if __name__ == "__main__":
    unittest.main()
