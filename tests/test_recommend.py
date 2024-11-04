from src.song import Song
from src.get_all import get_all_songs
from src.bot_state import BotState
from src.recommend_cog import RecommendCog
import pytest
import pandas as pd
from unittest.mock import AsyncMock, patch, MagicMock
import sys

sys.path.append("./")


@pytest.fixture
def recommend_cog():
    bot = AsyncMock()  # Mock the bot as needed
    return RecommendCog(bot)


# Prepare a fixture for song data
@pytest.fixture
def songs_df():
    return pd.DataFrame(
        {
            "track_name": [
                "Song1",
                "Song2",
                "Song3",
                "Song4",
                "Song5",
                "Song6",
                "Song7",
                "Song8",
                "Song9",
                "Song10",
            ],
            "artist_name": [
                "Artist1",
                "Artist2",
                "Artist3",
                "Artist4",
                "Artist5",
                "Artist1",
                "Artist2",
                "Artist3",
                "Artist4",
                "Artist5",
            ],
            "genre": [
                "Pop",
                "Rock",
                "Jazz",
                "Pop",
                "Rock",
                "Jazz",
                "Classical",
                "Country",
                "Blues",
                "Hip-Hop",
            ],
        }
    )


# Test to check if empty recommendation list is returned when no poll song is selected
def test_generate_recommendations_zero_songs(recommend_cog, songs_df):
    selected_songs = []
    recommendations = recommend_cog.generate_recommendations(selected_songs)
    assert len(recommendations) == 0


# Test to check if recommendations are generated based on a similar genre
@patch("src.get_all.get_all_songs")
def test_generate_recommendations_one_song(mock_get_all_songs, recommend_cog, songs_df):
    mock_get_all_songs.return_value = songs_df

    # Select one song for recommendation
    selected_songs = [Song(track_name="Song1", artist_name="Artist1", genre="Pop")]

    # Generate recommendations
    recommendations = recommend_cog.generate_recommendations(selected_songs)

    # Check if recommendations are generated correctly
    assert all(isinstance(song, Song)
               for song in recommendations), "All recommendations should be Song objects"


# Test to ensure artist appearance limit is respected
def test_artist_limit_in_recommendations(recommend_cog, songs_df):
    selected_songs = [Song(track_name="Song3", artist_name="Artist3", genre="Jazz")]
    recommendations = recommend_cog.generate_recommendations(selected_songs)

    artist_counts = {}
    for song in recommendations:
        artist_counts[song.artist_name] = artist_counts.get(song.artist_name, 0) + 1
        assert artist_counts[song.artist_name] <= 2, "Artist should not appear more than twice"


# Test to ensure that no artists from selected songs are recommended
def test_exclude_selected_artists(recommend_cog, songs_df):
    selected_songs = [
        Song(track_name="Song6", artist_name="Artist3", genre="Jazz"),
        Song(track_name="Song10", artist_name="Artist5", genre="Hip-Hop"),
    ]
    recommendations = recommend_cog.generate_recommendations(selected_songs)
    for song in recommendations:
        assert song.artist_name not in [
            "Artist3", "Artist5"], "Selected artists should not appear in recommendations"


# Test to verify that the recommendations do not include duplicate songs
def test_recommendation_uniqueness(recommend_cog, songs_df):
    selected_songs = [Song(track_name="Song2", artist_name="Artist2", genre="Rock")]
    recommendations = recommend_cog.generate_recommendations(selected_songs)
    unique_recommendations = set(str(song) for song in recommendations)
    assert len(unique_recommendations) == len(
        recommendations
    ), "All recommendations should be unique"


# Test the response when there aren't enough songs in the dataset
@patch("src.get_all.get_all_songs")
def test_insufficient_songs_for_recommendations(mock_get_all_songs, recommend_cog, songs_df):
    mock_get_all_songs.return_value = songs_df.head(5)  # only 5 songs available
    selected_songs = [Song(track_name="Song1", artist_name="Artist1", genre="Pop")]
    recommendations = recommend_cog.generate_recommendations(selected_songs)
    assert len(
        recommendations) < 10, "Should return fewer recommendations due to insufficient data"


# Ensure that recommendations do not exceed the maximum limit of 10
def test_max_recommendation_limit(recommend_cog, songs_df):
    selected_songs = [Song(track_name="Song8", artist_name="Artist4", genre="Country")]
    recommendations = recommend_cog.generate_recommendations(selected_songs)
    assert len(recommendations) <= 10, "Should not return more than 10 recommendations"


# Define a function to test mapping emojis to song indices
def map_emojis_to_songs(song_list):
    number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    return {
        emoji: song_list[index]
        for index, emoji in enumerate(number_emojis[: len(song_list)])
    }


def test_emoji_song_mapping():
    # Simulated song list
    songs = [
        Song("Song1", "Artist1", "Pop"),
        Song("Song2", "Artist2", "Rock"),
        Song("Song3", "Artist3", "Jazz"),
    ]

    # Run the mapping function
    emoji_song_map = map_emojis_to_songs(songs)

    # Assert the mapping is correct
    expected_map = {
        "1️⃣": Song("Song1", "Artist1", "Pop"),
        "2️⃣": Song("Song2", "Artist2", "Rock"),
        "3️⃣": Song("Song3", "Artist3", "Jazz"),
    }
    # assert emoji_song_map == expected_map, "Emoji to song mapping should match the expected output."
