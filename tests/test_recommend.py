import pytest
import pandas as pd
from unittest.mock import AsyncMock, MagicMock
import sys

sys.path.append("./")

from src.recommend_cog import RecommendCog
from src.bot_state import BotState

# Prepare a fixture for song data
@pytest.fixture
def songs_df():
    return pd.DataFrame({
        'track_name': ['Song1', 'Song2', 'Song3', 'Song4', 'Song5', 'Song6', 'Song7', 'Song8', 'Song9', 'Song10'],
        'artist_name': ['Artist1', 'Artist2', 'Artist3', 'Artist4', 'Artist5', 'Artist1', 'Artist2', 'Artist3', 'Artist4', 'Artist5'],
        'genre': ['Pop', 'Rock', 'Jazz', 'Pop', 'Rock', 'Jazz', 'Classical', 'Country', 'Blues', 'Hip-Hop']
    })

