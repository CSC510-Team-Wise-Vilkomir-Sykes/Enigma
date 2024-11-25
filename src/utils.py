"""
helper_functions.py

What:
    The `helper_functions` module provides essential utility functions that facilitate various operations within the Discord bot. These functions include searching for songs on YouTube and generating a random selection of songs for user polls. By abstracting these common tasks, the module ensures code reusability, readability, and maintainability across different components of the bot.

Why:
    Efficiently managing song searches and generating randomized song selections are critical for delivering a seamless user experience in a music recommendation system. The `helper_functions` module streamlines these processes, enabling the bot to quickly fetch relevant song links and present diverse song options to users. This enhances the bot's responsiveness and ensures that users receive timely and varied recommendations, thereby increasing engagement and satisfaction within the Discord community.

How:
    - **searchSong Function**: Utilizes the `youtubesearchpython` library to search for a given song name on YouTube and retrieves the URL of the top result. This function is essential for fetching playable links that the bot can stream in voice channels.

    - **random_25 Function**: Leverages pandas to sample a diverse set of 25 songs from the available dataset. By grouping songs by genre and selecting a subset, it ensures a balanced and varied selection for user polls, promoting discovery across different musical styles.

    - **Global Variable `all_songs`**: Preprocesses the complete song dataset by selecting relevant columns (`track_name`, `artist`, `genre`) and storing them in a DataFrame. This prepared dataset serves as the foundation for the `random_25` function to generate randomized song selections efficiently.

Example Use Cases:
    1. **Song Playback**: When a user requests to play a specific song, the bot uses `searchSong` to find the YouTube link and streams the audio in the voice channel.

    2. **Creating Polls for Recommendations**: To generate a poll for user preferences, the bot invokes `random_25` to select a diverse set of songs, ensuring that users are exposed to a variety of genres and artists.

    3. **Automated Song Suggestions**: The bot periodically suggests new songs to users by combining the functionalities of `searchSong` and `random_25`, enhancing the discovery of new music tailored to user tastes.

Classes:
    None. This module exclusively contains standalone functions and global variables.

Functions:
    - searchSong(name_song):
        Searches for the specified song on YouTube and returns the URL of the top search result.

    - random_25():
        Generates and returns a randomized selection of 25 songs from the available dataset, ensuring diversity across different genres.

Dependencies:
    - youtubesearchpython: Facilitates searching for videos on YouTube based on query strings.
    - pandas: Provides data manipulation and analysis capabilities, particularly for handling song datasets.
    - src.get_all: Custom module that supplies access to the filtered songs dataset.

Usage:
    To utilize the helper functions within the Discord bot, import them as needed in other modules. For example, to search for a song and retrieve its YouTube URL:

    ```python
    from helper_functions import searchSong

    song_url = searchSong("Shape of You")
    print(song_url)  # Outputs the YouTube URL of the top search result for "Shape of You"
    ```

    To generate a random selection of 25 songs for a poll:

    ```python
    from helper_functions import random_25

    poll_songs = random_25()
    print(poll_songs)
    # Outputs a DataFrame containing 25 randomly selected songs across different genres
    ```

Notes:
    - The `searchSong` function currently retrieves only the top search result. For enhanced functionality, consider handling cases where no results are found or allowing the selection of multiple search results.

    - The `random_25` function assumes that the `filtered_songs` function returns a DataFrame containing at least 25 songs across various genres. Ensure that the dataset is sufficiently large and diverse to support this operation.

    - Error handling is minimal in these functions. For production use, incorporate try-except blocks to manage potential exceptions, such as network issues or unexpected data formats.

    - The `all_songs` global variable preprocesses the song dataset upon module import. If the underlying data changes dynamically, consider updating this variable accordingly or converting it into a function to fetch the latest data as needed.

    - Future enhancements could include adding parameters to `random_25` to allow for different sample sizes or genre-specific selections based on user preferences.
"""

from youtubesearchpython import VideosSearch
from src.get_all import filtered_songs

"""
This function searches for the specified song on YouTube and returns the URL of the top search result.
"""


def searchSong(name_song):
	"""
	What:
		The `searchSong` function searches for a given song name on YouTube and retrieves the URL of the top search result. This URL can then be used to stream the song in a Discord voice channel.

	Why:
		Obtaining the direct YouTube link for a song is essential for streaming audio within Discord. By automating the search process, the bot can efficiently find and play the requested songs without manual intervention.

	How:
		- Utilizes the `VideosSearch` class from the `youtubesearchpython` library to perform a search query for the specified song name.
		- Limits the search results to the top entry.
		- Extracts the URL of the first video in the search results.
		- Returns the extracted YouTube link.

	Example:
		```python
		from helper_functions import searchSong

		song_url = searchSong("Shape of You")
		print(song_url)  # Outputs the YouTube URL for "Shape of You" by Ed Sheeran
		```

	Parameters:
		name_song (str): The name of the song to search for on YouTube.

	Returns:
		str: The YouTube URL of the top search result for the specified song.
	"""
	videosSearch = VideosSearch(name_song, limit=1)
	result = videosSearch.result()
	link = result["result"][0]["link"]
	return link


all_songs = filtered_songs()[["track_name", "artist", "genre"]]
"""
This global variable `all_songs` holds a DataFrame containing the track name, artist, and genre of all filtered songs. It serves as the data source for generating randomized song selections.
"""


"""
This function returns a random selection of 25 songs for generating polls for the user.
"""


def random_25():
	"""
	What:
		The `random_25` function generates and returns a randomized selection of 25 songs from the available dataset. This selection is intended for creating user polls, ensuring that users are presented with a diverse and balanced set of song options.

	Why:
		Presenting a varied selection of songs across different genres enhances user engagement by catering to a wide range of musical preferences. By randomizing the selection, the function ensures fairness and prevents bias towards any particular genre or artist.

	How:
		- Shuffles the `all_songs` DataFrame to randomize the order of songs.
		- Groups the shuffled songs by genre and selects the top entry from each group to ensure genre diversity.
		- Samples 25 songs from the grouped selection to create the final randomized list.
		- Returns the resulting DataFrame containing the 25 selected songs.

	Example:
		```python
		from helper_functions import random_25

		poll_songs = random_25()
		print(poll_songs)
		# Outputs a DataFrame with 25 randomly selected songs across various genres
		```

	Returns:
		pandas.DataFrame: A DataFrame containing 25 randomly selected songs with their track names, artists, and genres.
	"""
	random_songs = (all_songs.sample(frac=1).groupby("genre").head(1)).sample(25)
	return random_songs
