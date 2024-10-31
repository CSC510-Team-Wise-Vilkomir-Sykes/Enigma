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






