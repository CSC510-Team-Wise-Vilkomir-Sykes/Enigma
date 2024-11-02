import pytest
import pandas as pd
from unittest.mock import AsyncMock, patch, MagicMock
import sys

sys.path.append("./")

from src.recommend_cog import RecommendCog
from src.bot_state import BotState
from src.get_all import *

@pytest.fixture
def recommend_cog():
    bot = AsyncMock()  # Mock the bot as needed
    return RecommendCog(bot)

# Prepare a fixture for song data
@pytest.fixture
def songs_df():
    return pd.DataFrame({
        'track_name': ['Song1', 'Song2', 'Song3', 'Song4', 'Song5', 'Song6', 'Song7', 'Song8', 'Song9', 'Song10'],
        'artist_name': ['Artist1', 'Artist2', 'Artist3', 'Artist4', 'Artist5', 'Artist1', 'Artist2', 'Artist3', 'Artist4', 'Artist5'],
        'genre': ['Pop', 'Rock', 'Jazz', 'Pop', 'Rock', 'Jazz', 'Classical', 'Country', 'Blues', 'Hip-Hop']
    })

# Test to check if empty recommendation list returned when no poll song selected
def test_generate_recommendations_zero_songs(songs_df):
    selected_songs = []
    recommendations = RecommendCog.generate_recommendations(songs_df, selected_songs)
    assert len(recommendations) == 0

# Test to check if 1 recommendations are returned because of the similar genre
@patch('src.recommend_cog.get_all_songs')
def test_generate_recommendations_ten_songs(mock_get_all_songs, songs_df):
    # Setup the mock to return the predefined DataFrame
    mock_get_all_songs.return_value = songs_df

    # Create an instance of the RecommendCog with a mock bot object
    bot = MagicMock()
    cog = RecommendCog(bot)

    # Define selected songs that would allow for 10 recommendations
    selected_songs = [{'track_name': 'Song1', 'artist_name': 'Artist3', 'genre': 'Blues'}]

    # Call the method under test
    recommendations = cog.generate_recommendations(selected_songs)
    print(recommendations)
    # Check if 10 recommendations are returned
    assert len(recommendations) == 1, "Should return exactly 1 recommendations"

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

# Test to verify that the recommendations do not include duplicate songs
def test_recommendation_uniqueness(songs_df):
    selected_songs = [{'track_name': 'Song2', 'artist_name': 'Artist2', 'genre': 'Rock'}]
    recommendations = RecommendCog.generate_recommendations(songs_df, selected_songs)
    unique_recommendations = set(recommendations)
    assert len(unique_recommendations) == len(recommendations), "All recommendations should be unique"

def test_exclude_specific_genres(songs_df):
    selected_songs = [{'track_name': 'Song7', 'artist_name': 'Artist2', 'genre': 'Classical'}]
    recommendations = RecommendCog.generate_recommendations(songs_df, selected_songs)
    for rec in recommendations:
        assert 'Classical' not in rec, "Classical genre should be excluded from recommendations"

# Test the response when there aren't enough songs in the dataset
@patch('src.recommend_cog.get_all_songs')
def test_insufficient_songs_for_recommendations(mock_get_all_songs, songs_df):
    mock_get_all_songs.return_value = songs_df.head(5)  # only 5 songs available
    selected_songs = [{'track_name': 'Song1', 'artist_name': 'Artist1', 'genre': 'Pop'}]
    recommendations = RecommendCog.generate_recommendations(songs_df, selected_songs)
    assert len(recommendations) < 10, "Should return fewer recommendations due to insufficient data"

# Ensure that even if more recommendations could be made
def test_max_recommendation_limit(songs_df):
    selected_songs = [{'track_name': 'Song8', 'artist_name': 'Artist4', 'genre': 'Country'}]
    recommendations = RecommendCog.generate_recommendations(songs_df, selected_songs)
    assert len(recommendations) <= 10, "Should not return more than 10 recommendations"

# Define a function to test mapping emojis to song indices
def map_emojis_to_songs(song_list):
    number_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    return {emoji: song_list[index] for index, emoji in enumerate(number_emojis[:len(song_list)])}

def test_emoji_song_mapping():
    # Simulated song list
    songs = [
        {'track_name': 'Song1', 'artist_name': 'Artist1', 'genre': 'Pop'},
        {'track_name': 'Song2', 'artist_name': 'Artist2', 'genre': 'Rock'},
        {'track_name': 'Song3', 'artist_name': 'Artist3', 'genre': 'Jazz'}
    ]

    # Run the mapping function
    emoji_song_map = map_emojis_to_songs(songs)

    # Assert the mapping is correct
    expected_map = {
        '1️⃣': {'track_name': 'Song1', 'artist_name': 'Artist1', 'genre': 'Pop'},
        '2️⃣': {'track_name': 'Song2', 'artist_name': 'Artist2', 'genre': 'Rock'},
        '3️⃣': {'track_name': 'Song3', 'artist_name': 'Artist3', 'genre': 'Jazz'}
    }
    assert emoji_song_map == expected_map, "Emoji to song mapping should match the expected output."
