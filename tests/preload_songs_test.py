import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from src.song_queue_cog import SongQueueCog  # Adjust the import path as necessary
from src.bot_state import BotState
from src.song import Song
import asyncio

class TestPreloadSongs(unittest.IsolatedAsyncioTestCase):
	def setUp(self):
		# Initialize a mock bot and cog
		self.bot = MagicMock()
		self.cog = SongQueueCog(self.bot)

		# Mock the BotState.song_queue
		BotState.song_queue = []

		# Mock the logger and log_and_send
		BotState.log_and_send = AsyncMock()

		# Mock ytdl.extract_info
		self.patcher = patch('src.song_queue_cog.ytdl.extract_info')
		self.mock_extract_info = self.patcher.start()

	def tearDown(self):
		self.patcher.stop()

	async def test_preload_songs_empty_queue(self):
		"""Ensure no preloading occurs when the queue is empty."""
		ctx = MagicMock()
		BotState.song_queue = []

		await self.cog.preload_songs(ctx)

		self.mock_extract_info.assert_not_called()
		BotState.log_and_send.assert_not_called()

	async def test_preload_single_song_success(self):
		"""Preload a single song successfully."""
		ctx = MagicMock()
		BotState.song_queue = [Song(track_name="Song 1", url=None)]

		self.mock_extract_info.return_value = {"entries": [{"url": "http://url1.com"}]}

		await self.cog.preload_songs(ctx)

		self.assertEqual(BotState.song_queue[0].url, "http://url1.com")
		self.mock_extract_info.assert_called_once_with("ytsearch:Song 1", download=False)
		BotState.log_and_send.assert_not_called()

	async def test_preload_multiple_songs_less_than_limit(self):
		"""Preload multiple songs when queue size is below preload limit."""
		ctx = MagicMock()
		BotState.song_queue = [
			Song(track_name="Song 1", url=None),
			Song(track_name="Song 2", url=None),
			Song(track_name="Song 3", url=None)
		]

		self.mock_extract_info.side_effect = [
			{"entries": [{"url": "http://url1.com"}]},
			{"entries": [{"url": "http://url2.com"}]},
			{"entries": [{"url": "http://url3.com"}]}
		]

		await self.cog.preload_songs(ctx)

		for i in range(3):
			self.assertEqual(BotState.song_queue[i].url, f"http://url{i+1}.com")
		self.assertEqual(self.mock_extract_info.call_count, 3)
		BotState.log_and_send.assert_not_called()

	async def test_preload_multiple_songs_equal_to_limit(self):
		"""Preload songs exactly up to the preload limit."""
		ctx = MagicMock()
		BotState.song_queue = [
			Song(track_name=f"Song {i}", url=None) for i in range(1, 6)
		]

		self.mock_extract_info.side_effect = [
			{"entries": [{"url": f"http://url{i}.com"}]} for i in range(1, 6)
		]

		await self.cog.preload_songs(ctx)

		for i in range(5):
			self.assertEqual(BotState.song_queue[i].url, f"http://url{i+1}.com")
		self.assertEqual(self.mock_extract_info.call_count, 5)
		BotState.log_and_send.assert_not_called()

	async def test_preload_multiple_songs_exceeding_limit(self):
		"""Ensure only up to the preload limit are preloaded when queue exceeds the limit."""
		ctx = MagicMock()
		BotState.song_queue = [
			Song(track_name=f"Song {i}", url=None) for i in range(1, 8)
		]

		self.mock_extract_info.side_effect = [
			{"entries": [{"url": f"http://url{i}.com"}]} for i in range(1, 6)
		]

		await self.cog.preload_songs(ctx)

		for i in range(5):
			self.assertEqual(BotState.song_queue[i].url, f"http://url{i+1}.com")
		for i in range(5, 7):
			self.assertIsNone(BotState.song_queue[i].url)
		self.assertEqual(self.mock_extract_info.call_count, 5)
		BotState.log_and_send.assert_not_called()

	async def test_preload_some_songs_already_preloaded(self):
		"""Preload only songs that haven't been preloaded yet."""
		ctx = MagicMock()
		BotState.song_queue = [
			Song(track_name="Song 1", url="http://url1.com"),
			Song(track_name="Song 2", url=None),
			Song(track_name="Song 3", url="http://url3.com"),
			Song(track_name="Song 4", url=None),
			Song(track_name="Song 5", url=None)
		]

		self.mock_extract_info.side_effect = [
			{"entries": [{"url": "http://url2.com"}]},
			{"entries": [{"url": "http://url4.com"}]},
			{"entries": [{"url": "http://url5.com"}]}
		]

		await self.cog.preload_songs(ctx)

		self.assertEqual(BotState.song_queue[0].url, "http://url1.com")
		self.assertEqual(BotState.song_queue[1].url, "http://url2.com")
		self.assertEqual(BotState.song_queue[2].url, "http://url3.com")
		self.assertEqual(BotState.song_queue[3].url, "http://url4.com")
		self.assertEqual(BotState.song_queue[4].url, "http://url5.com")
		self.assertEqual(self.mock_extract_info.call_count, 3)
		BotState.log_and_send.assert_not_called()

	async def test_preload_all_songs_already_preloaded(self):
		"""Ensure no action is taken when all songs are already preloaded."""
		ctx = MagicMock()
		BotState.song_queue = [
			Song(track_name=f"Song {i}", url=f"http://url{i}.com") for i in range(1, 6)
		]

		await self.cog.preload_songs(ctx)

		self.mock_extract_info.assert_not_called()
		BotState.log_and_send.assert_not_called()

	async def test_preload_song_failure(self):
		"""Handle and log errors when preloading a song fails."""
		ctx = MagicMock()
		BotState.song_queue = [
			Song(track_name="Song 1", url=None),
			Song(track_name="Song 2", url=None)
		]

		self.mock_extract_info.side_effect = [
			{"entries": [{"url": "http://url1.com"}]},
			Exception("YTDL error")
		]

		await self.cog.preload_songs(ctx)

		self.assertEqual(BotState.song_queue[0].url, "http://url1.com")
		self.assertIsNone(BotState.song_queue[1].url)
		self.assertEqual(self.mock_extract_info.call_count, 2)
		BotState.log_and_send.assert_called_once_with(ctx, "Error preloading song Song 2: YTDL error")

	async def test_preload_invalid_track_name(self):
		"""Handle cases where a song has an invalid or empty track name."""
		ctx = MagicMock()
		BotState.song_queue = [Song(track_name="", url=None)]

		self.mock_extract_info.side_effect = Exception("Invalid track name")

		await self.cog.preload_songs(ctx)

		self.assertIsNone(BotState.song_queue[0].url)
		self.mock_extract_info.assert_called_once_with("ytsearch:", download=False)
		BotState.log_and_send.assert_called_once_with(ctx, "Error preloading song : Invalid track name")

	async def test_preload_special_characters_in_track_name(self):
		"""Successfully preload songs with special characters in their names."""
		ctx = MagicMock()
		BotState.song_queue = [Song(track_name="Søng 🚀", url=None)]

		self.mock_extract_info.return_value = {"entries": [{"url": "http://url_special.com"}]}

		await self.cog.preload_songs(ctx)

		self.assertEqual(BotState.song_queue[0].url, "http://url_special.com")
		self.mock_extract_info.assert_called_once_with("ytsearch:Søng 🚀", download=False)
		BotState.log_and_send.assert_not_called()

	async def test_preload_unicode_characters_in_track_name(self):
		"""Successfully preload songs with Unicode characters."""
		ctx = MagicMock()
		BotState.song_queue = [Song(track_name="Søng 🚀✨", url=None)]

		self.mock_extract_info.return_value = {"entries": [{"url": "http://url_unicode.com"}]}

		await self.cog.preload_songs(ctx)

		self.assertEqual(BotState.song_queue[0].url, "http://url_unicode.com")
		self.mock_extract_info.assert_called_once_with("ytsearch:Søng 🚀✨", download=False)
		BotState.log_and_send.assert_not_called()

	async def test_preload_duplicate_track_names(self):
		"""Ensure each song with duplicate names is preloaded independently."""
		ctx = MagicMock()
		BotState.song_queue = [
			Song(track_name="Duplicate Song", url=None),
			Song(track_name="Duplicate Song", url=None)
		]

		self.mock_extract_info.side_effect = [
			{"entries": [{"url": "http://url1.com"}]},
			{"entries": [{"url": "http://url2.com"}]}
		]

		await self.cog.preload_songs(ctx)

		self.assertEqual(BotState.song_queue[0].url, "http://url1.com")
		self.assertEqual(BotState.song_queue[1].url, "http://url2.com")
		self.assertEqual(self.mock_extract_info.call_count, 2)
		BotState.log_and_send.assert_not_called()

	async def test_preload_non_youtube_urls(self):
		"""Handle preloading when songs might have non-YouTube URLs."""
		ctx = MagicMock()
		BotState.song_queue = [Song(track_name="Non-YouTube Song", url=None)]

		self.mock_extract_info.return_value = {"entries": [{"url": "http://nonyoutube.com/audio"}]}

		await self.cog.preload_songs(ctx)

		self.assertEqual(BotState.song_queue[0].url, "http://nonyoutube.com/audio")
		self.mock_extract_info.assert_called_once_with("ytsearch:Non-YouTube Song", download=False)
		BotState.log_and_send.assert_not_called()

	async def test_preload_partial_success(self):
		"""Some songs preload successfully while others fail."""
		ctx = MagicMock()
		BotState.song_queue = [
			Song(track_name="Song 1", url=None),
			Song(track_name="Song 2", url=None),
			Song(track_name="Song 3", url=None)
		]

		self.mock_extract_info.side_effect = [
			{"entries": [{"url": "http://url1.com"}]},
			Exception("YTDL failure"),
			{"entries": [{"url": "http://url3.com"}]}
		]

		await self.cog.preload_songs(ctx)

		self.assertEqual(BotState.song_queue[0].url, "http://url1.com")
		self.assertIsNone(BotState.song_queue[1].url)
		self.assertEqual(BotState.song_queue[2].url, "http://url3.com")
		self.assertEqual(self.mock_extract_info.call_count, 3)
		BotState.log_and_send.assert_called_once_with(ctx, "Error preloading song Song 2: YTDL failure")

	async def test_preload_large_track_names(self):
		"""Successfully handle and preload songs with very long track names."""
		ctx = MagicMock()
		long_track_name = "A" * 1000  # Very long track name
		BotState.song_queue = [Song(track_name=long_track_name, url=None)]

		self.mock_extract_info.return_value = {"entries": [{"url": "http://url_long.com"}]}

		await self.cog.preload_songs(ctx)

		self.assertEqual(BotState.song_queue[0].url, "http://url_long.com")
		self.mock_extract_info.assert_called_once_with(f"ytsearch:{long_track_name}", download=False)
		BotState.log_and_send.assert_not_called()

	async def test_preload_whitespace_track_name(self):
		"""Handle songs whose track names consist only of whitespace."""
		ctx = MagicMock()
		BotState.song_queue = [Song(track_name="   ", url=None)]

		self.mock_extract_info.side_effect = Exception("Invalid track name")

		await self.cog.preload_songs(ctx)

		self.assertIsNone(BotState.song_queue[0].url)
		self.mock_extract_info.assert_called_once_with("ytsearch:   ", download=False)
		BotState.log_and_send.assert_called_once_with(ctx, "Error preloading song    : Invalid track name")

	async def test_preload_limit_enforcement(self):
		"""Strictly enforce the preload limit of 5 songs."""
		ctx = MagicMock()
		BotState.song_queue = [
			Song(track_name=f"Song {i}", url=None) for i in range(1, 10)
		]

		self.mock_extract_info.side_effect = [
			{"entries": [{"url": f"http://url{i}.com"}]} for i in range(1, 6)
		]

		await self.cog.preload_songs(ctx)

		for i in range(5):
			self.assertEqual(BotState.song_queue[i].url, f"http://url{i+1}.com")
		for i in range(5, 9):
			self.assertIsNone(BotState.song_queue[i].url)
		self.assertEqual(self.mock_extract_info.call_count, 5)
		BotState.log_and_send.assert_not_called()

	async def test_preload_non_list_song_queue(self):
		"""Handle scenarios where `BotState.song_queue` is not a list."""
		ctx = MagicMock()
		BotState.song_queue = "Not a list"

		with self.assertRaises(AttributeError):
			await self.cog.preload_songs(ctx)

		self.mock_extract_info.assert_not_called()
		BotState.log_and_send.assert_not_called()

	async def test_preload_no_entries_returned(self):
		"""Handle cases where extract_info returns no entries."""
		ctx = MagicMock()
		BotState.song_queue = [Song(track_name="Song 1", url=None)]

		# Mock extract_info to return empty 'entries'
		self.mock_extract_info.return_value = {"entries": []}

		await self.cog.preload_songs(ctx)

		# Assert that the song's URL remains None
		self.assertIsNone(BotState.song_queue[0].url)

		# Assert that extract_info was called once with the correct query
		self.mock_extract_info.assert_called_once_with("ytsearch:Song 1", download=False)

		# Assert that log_and_send was called once with the appropriate error message
		expected_error_message = "Error preloading song Song 1: list index out of range"
		BotState.log_and_send.assert_called_once_with(ctx, expected_error_message)

	async def test_preload_unexpected_extract_info_structure(self):
		"""Handle cases where extract_info returns an unexpected structure."""
		ctx = MagicMock()
		BotState.song_queue = [Song(track_name="Song 2", url=None)]

		# Mock extract_info to return data without 'entries' key
		self.mock_extract_info.return_value = {}

		await self.cog.preload_songs(ctx)

		# Assert that the song's URL remains None
		self.assertIsNone(BotState.song_queue[0].url)

		# Assert that extract_info was called once with the correct query
		self.mock_extract_info.assert_called_once_with("ytsearch:Song 2", download=False)

		# Assert that log_and_send was called once with the appropriate error message
		expected_error_message = "Error preloading song Song 2: 'entries'"
		BotState.log_and_send.assert_called_once_with(ctx, expected_error_message)
