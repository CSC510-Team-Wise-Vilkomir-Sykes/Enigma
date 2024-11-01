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

# Test to check if 10 recommendations are returned
def test_generate_recommendations_ten_songs(songs_df):
    selected_songs = [{'track_name': 'Song1', 'artist_name': 'Artist1', 'genre': 'Pop'}]
    recommendations = RecommendCog.generate_recommendations(songs_df, selected_songs)
    assert len(recommendations) == 10

# Test to ensure artist appearance limit is respected
def test_artist_limit_in_recommendations(songs_df):
    selected_songs = [{'track_name': 'Song3', 'artist_name': 'Artist3', 'genre': 'Jazz'}]
    recommendations = RecommendCog.generate_recommendations(songs_df, selected_songs)
    artist_counts = {}
    for rec in recommendations:
        artist = rec.split(" by ")[1].split(" (")[0]
        artist_counts[artist] = artist_counts.get(artist, 0) + 1
        assert artist_counts[artist] <= 2

# Test to ensure that no artists from selected songs are recommended
def test_exclude_selected_artists(songs_df):
    selected_songs = [{'track_name': 'Song6', 'artist_name': 'Artist3', 'genre': 'Jazz'}, {'track_name': 'Song10', 'artist_name': 'Artist5', 'genre': 'Hip-Hop'}]
    recommendations = RecommendCog.generate_recommendations(songs_df, selected_songs)
    for rec in recommendations:
        assert 'Artist3' not in rec and 'Artist5' not in rec