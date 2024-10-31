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
    all_songs = pd.read_csv("./data/songs.csv")
    sampled_songs = (all_songs.groupby('genre').head(1)).sample(n, replace=True)  # Ensure unique genres
    return sampled_songs


