"""
This module handles all data operations related to songs, including retrieving song details, filtering songs
by attributes, and recommending songs for polls.

**Why**:
Provides centralized functions for managing and accessing song data, enabling features like recommendations
and poll generation.

**How**:
- Load song datasets using `pandas`.
- Perform operations such as filtering and sampling to meet specific needs, like generating polls.

**Functions**:
1. `filtered_songs`: Returns filtered song attributes.
2. `get_all_songs`: Returns all songs in the dataset.
3. `get_songs_by_genre`: Returns a sample of songs from different genres for user polls.
"""

import pandas as pd


def filtered_songs():
	"""
	Retrieves a filtered dataset of songs containing only the track name, artist, year, and genre.

	**What**:
	- Loads a CSV file containing song data.
	- Filters columns to include `track_name`, `artist`, `year`, and `genre`.

	**Why**:
	- Provides a simplified dataset focused on key song attributes for quick access and display.

	**How**:
	- Uses `pandas` to load and filter data from a CSV file.

	:return: A DataFrame containing the filtered song attributes.
	:rtype: pandas.DataFrame

	Example:
	```
	songs = filtered_songs()
	print(songs.head())
	```
	"""
	all_songs = pd.read_csv("./data/songs.csv")
	all_songs = all_songs.filter(["track_name", "artist", "year", "genre"])
	return all_songs


def get_all_songs():
	"""
	Retrieves all songs from the dataset.

	**What**:
	- Loads a comprehensive song dataset from a CSV file.

	**Why**:
	- Provides access to the entire dataset for operations like detailed analysis or recommendation generation.

	**How**:
	- Uses `pandas` to load the dataset.

	:return: A DataFrame containing all songs in the dataset.
	:rtype: pandas.DataFrame

	Example:
	```
	all_songs = get_all_songs()
	print(all_songs.info())
	```
	"""
	all_songs = pd.read_csv("./data/tcc_ceds_music.csv")
	return all_songs


def get_songs_by_genre(n=10):
	"""
	Retrieves a sample of `n` songs across different genres for generating a poll.

	**What**:
	- Samples unique songs from the dataset, ensuring a diverse selection of genres.

	**Why**:
	- Generates a list of songs for polls, allowing users to select preferences from a curated set.

	**How**:
	- Removes duplicates based on `track_name` and `artist_name`.
	- Randomly samples songs until the desired count is reached.

	:param n: Number of songs to sample.
	:type n: int, optional (default: 10)
	:return: A DataFrame containing the sampled songs.
	:rtype: pandas.DataFrame

	Example:
	```
	sampled_songs = get_songs_by_genre(10)
	print(sampled_songs)
	```
	"""
	all_songs = pd.read_csv("./data/tcc_ceds_music.csv")
	unique_songs = all_songs.drop_duplicates(subset=["track_name", "artist_name"])
	sampled_songs = pd.DataFrame()  # Use a DataFrame to collect samples

	# Track added songs to avoid duplicates
	sampled_ids = set()

	while len(sampled_songs) < n:
		song = unique_songs.sample(1)
		# Create a unique identifier for the song
		song_id = (song["track_name"].iloc[0], song["artist_name"].iloc[0])

		if song_id not in sampled_ids:
			sampled_ids.add(song_id)
			# Safely concatenate the sampled song
			sampled_songs = pd.concat([sampled_songs, song])

	return sampled_songs
