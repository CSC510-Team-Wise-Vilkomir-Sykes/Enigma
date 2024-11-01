import pytest
import pandas as pd
from discord.ext import commands
from unittest.mock import patch, MagicMock
from discord import Intents

import sys
sys.path.append("./")

from src.recommend_cog import *
from src.get_all import *

def generate_test_songs_data():
    # Generate a DataFrame simulating songs with different genres
    data = {
        'track_name': ['Song1', 'Song2', 'Song3', 'Song4', 'Song5', 'Song6', 'Song7', 'Song8', 'Song9', 'Song10'],
        'artist_name': ['Artist1', 'Artist2', 'Artist3', 'Artist4', 'Artist5', 'Artist6', 'Artist7', 'Artist8', 'Artist9', 'Artist10'],
        'genre': ['Pop', 'Rock', 'Jazz', 'Pop', 'Rock', 'Jazz', 'Classical', 'Country', 'Blues', 'Hip-Hop']
    }
    return pd.DataFrame(data)

@pytest.fixture
def test_songs():
    return generate_test_songs_data()

@patch('pandas.read_csv')
def test_get_songs_by_genre_length(mock_read_csv, test_songs):
    mock_read_csv.return_value = test_songs
    
    # Call get_songs_by_genre with n=5
    result = get_songs_by_genre(5)
    assert len(result) == 5, "The function should return exactly 5 songs."

@patch('pandas.read_csv')
def test_get_songs_variety(mock_read_csv, test_songs):
    mock_read_csv.return_value = test_songs

    # Call get_songs_by_genre twice and check for variety in genre selection
    result1 = get_songs_by_genre(5)
    result2 = get_songs_by_genre(5)

    # This test checks if different songs are being fetched on different calls
    assert set(result1['track_name']) != set(result2['track_name']), "The selections should vary."



