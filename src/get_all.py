"""
This file is responsible for handling all data operations such as showing songs that the user can select.
Recommendation of songs filtering operations etc.
"""

import pandas as pd
import random

"""
This function returns songs and their track_name, artist, year and genre.
"""
def filtered_songs():
    all_songs = pd.read_csv("./data/songs.csv")
    all_songs = all_songs.filter(["track_name", "artist", "year", "genre"])
    return all_songs


"""
This function returns all songs in the dataset.
"""
def get_all_songs():
    all_songs = pd.read_csv("./data/tcc_ceds_music.csv")
    return all_songs


"""
This function returns 10 songs within different genre for generating the poll for the user
"""
def get_songs_by_genre(n=10):
    all_songs = pd.read_csv("./data/tcc_ceds_music.csv")
    unique_songs = all_songs.drop_duplicates(subset=['track_name', 'artist_name'])
    sampled_songs = pd.DataFrame()  # use a DataFrame to collect samples

    # to keep track of what has been added
    sampled_ids = set()

    while len(sampled_songs) < n:
        song = unique_songs.sample(1)
        # creating a tuple identifier
        song_id = (song['track_name'].iloc[0], song['artist_name'].iloc[0])

        if song_id not in sampled_ids:
            sampled_ids.add(song_id)
            # safely concatenate without duplication
            sampled_songs = pd.concat([sampled_songs, song])

    return sampled_songs


