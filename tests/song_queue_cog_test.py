import pytest
import unittest
import warnings
import sys

sys.path.append("./")

from src.song_queue_cog import *
warnings.filterwarnings("ignore")


@pytest.mark.asyncio
class Test_Song_Queue_Cog(unittest.TestCase):

    async def test_resume(self):
        result = await SongQueueCog.resume()
        assert result == "The bot was not playing anything before this. Use play command"

    async def test_stop(self):
        result = await SongQueueCog.stop()
        assert result == "The bot is not playing anything at the moment."

    async def test_play_song(self):
        result = await SongQueueCog.play_song()
        assert result == "The bot is not connected to a voice channel."

    async def test_handle_empty_queue(self):
        result = await SongQueueCog.handle_empty_queue()
        assert result == "No recommendations present. First generate recommendations using /poll"

    async def test_pause(self):
        result = await SongQueueCog.pause()
        assert result == "The bot is not playing anything at the moment."

    async def test_shuffle(self):
        result = await SongQueueCog.shuffle()
        assert result == "Playlist shuffled"

    async def test_add_song(self):
        result = await SongQueueCog.add_song()
        assert result == "Song added to queue"
