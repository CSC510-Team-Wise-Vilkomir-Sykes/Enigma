import unittest
from unittest.mock import MagicMock, patch
from src.bot_state import BotState

class TestVolumeMethods(unittest.TestCase):

    def setUp(self):
        # Initialize a mock logger for BotState
        BotState.logger = MagicMock()

    @patch("src.bot_state.BotState.logger")
    def test_set_volume_within_range(self, mock_logger):
        voice_client = MagicMock()
        voice_client.source = MagicMock()
        BotState.volume = 0.5  # Initial volume

        BotState.set_volume(voice_client, 0.8)

        self.assertEqual(BotState.volume, 0.8)
        self.assertEqual(voice_client.source.volume, 0.8)
        mock_logger.info.assert_called_with("Volume set to 80.0%")

    @patch("src.bot_state.BotState.logger")
    def test_set_volume_lower_bound(self, mock_logger):
        voice_client = MagicMock()
        voice_client.source = MagicMock()

        BotState.set_volume(voice_client, 0.0)

        self.assertEqual(BotState.volume, 0.0)
        self.assertEqual(voice_client.source.volume, 0.0)
        mock_logger.info.assert_called_with("Volume set to 0.0%")

    @patch("src.bot_state.BotState.logger")
    def test_set_volume_upper_bound(self, mock_logger):
        voice_client = MagicMock()
        voice_client.source = MagicMock()

        BotState.set_volume(voice_client, 1.0)

        self.assertEqual(BotState.volume, 1.0)
        self.assertEqual(voice_client.source.volume, 1.0)
        mock_logger.info.assert_called_with("Volume set to 100.0%")

    @patch("src.bot_state.BotState.logger")
    def test_set_volume_below_range(self, mock_logger):
        voice_client = MagicMock()
        voice_client.source = MagicMock()

        BotState.set_volume(voice_client, -0.1)

        self.assertNotEqual(BotState.volume, -0.1)
        mock_logger.warning.assert_called_with("Attempted to set invalid volume: -0.1")

    @patch("src.bot_state.BotState.logger")
    def test_set_volume_above_range(self, mock_logger):
        voice_client = MagicMock()
        voice_client.source = MagicMock()

        BotState.set_volume(voice_client, 1.1)

        self.assertNotEqual(BotState.volume, 1.1)
        mock_logger.warning.assert_called_with("Attempted to set invalid volume: 1.1")

    @patch("src.bot_state.BotState.logger")
    def test_set_volume_null_voice_client(self, mock_logger):
        voice_client = None
        BotState.set_volume(voice_client, 0.5)

        self.assertEqual(BotState.volume, 0.5)
        mock_logger.info.assert_called_with("Volume set to 50.0%")

    @patch("src.bot_state.BotState.logger")
    def test_set_volume_null_voice_client_source(self, mock_logger):
        voice_client = MagicMock()
        voice_client.source = None

        BotState.set_volume(voice_client, 0.5)

        self.assertEqual(BotState.volume, 0.5)
        mock_logger.info.assert_called_with("Volume set to 50.0%")

    def test_get_volume_default(self):
        BotState.volume = 0.5  # Default volume for testing
        result = BotState.get_volume()
        self.assertEqual(result, 0.5)

    def test_get_volume_after_set(self):
        BotState.volume = 0.75
        result = BotState.get_volume()
        self.assertEqual(result, 0.75)

    @patch("src.bot_state.BotState.logger")
    def test_set_volume_invalid_type(self, mock_logger):
        voice_client = MagicMock()
        with self.assertRaises(TypeError):
            BotState.set_volume(voice_client, "invalid")

    @patch("src.bot_state.BotState.logger")
    def test_set_volume_none(self, mock_logger):
        voice_client = MagicMock()
        with self.assertRaises(TypeError):
            BotState.set_volume(voice_client, None)

    @patch("src.bot_state.BotState.logger")
    def test_set_volume_no_voice_client(self, mock_logger):
        BotState.set_volume(None, 0.3)
        self.assertEqual(BotState.volume, 0.3)
        mock_logger.info.assert_called_with("Volume set to 30.0%")

    def test_get_volume_zero(self):
        BotState.volume = 0.0
        result = BotState.get_volume()
        self.assertEqual(result, 0.0)

    def test_get_volume_one(self):
        BotState.volume = 1.0
        result = BotState.get_volume()
        self.assertEqual(result, 1.0)

    def test_set_volume_persistence(self):
        voice_client = MagicMock()
        voice_client.source = MagicMock()

        # Test setting volume
        BotState.set_volume(voice_client, 0.6)

        # Verify volume is set correctly
        self.assertEqual(BotState.volume, 0.6)

        # Verify logger was called
        BotState.logger.info.assert_called_once_with("Volume set to 60.0%")

    @patch("src.bot_state.BotState.logger")
    def test_logger_call_on_valid_volume(self, mock_logger):
        voice_client = MagicMock()
        voice_client.source = MagicMock()

        BotState.set_volume(voice_client, 0.4)
        mock_logger.info.assert_called_once()

    @patch("src.bot_state.BotState.logger")
    def test_logger_call_on_invalid_volume(self, mock_logger):
        voice_client = MagicMock()

        BotState.set_volume(voice_client, -1.0)
        mock_logger.warning.assert_called_once()

    @patch("src.bot_state.BotState.logger")
    def test_set_volume_updates_correctly_multiple_times(self, mock_logger):
        voice_client = MagicMock()
        voice_client.source = MagicMock()

        BotState.set_volume(voice_client, 0.1)
        self.assertEqual(BotState.get_volume(), 0.1)

        BotState.set_volume(voice_client, 0.9)
        self.assertEqual(BotState.get_volume(), 0.9)

    def test_get_volume_returns_consistent_value(self):
        BotState.volume = 0.3
        self.assertEqual(BotState.get_volume(), 0.3)

    @patch("src.bot_state.BotState.logger")
    def test_set_volume_does_not_change_on_invalid_input(self, mock_logger):
        voice_client = MagicMock()
        BotState.volume = 0.7  # Initial valid volume

        BotState.set_volume(voice_client, -0.5)
        self.assertEqual(BotState.get_volume(), 0.7)
