"""
song.py

This module defines the Song class, which represents a music track with its associated details, such as
track name, artist name, and genre.
"""


class Song:
	def __init__(self, track_name, artist_name=None, genre=None):
		"""Initializes a new Song instance.

            Args:
                track_name (str): The name of the song.
                artist_name (str, optional): The name of the artist. Defaults to None if unknown.
                genre (str, optional): The genre of the song. Defaults to None if unspecified.
        """
		self.track_name = track_name  # The title of the song
		self.artist_name = artist_name  # The artist who performed the song
		self.genre = genre  # The genre of the song

	def __str__(self):
		"""Returns a formatted string representation of the song.

            If the artist name is available, the format will be '<track_name> by <artist_name>'.
            Otherwise, it will simply return the track name.

            Returns:
                str: The string representation of the song.
        """
		if self.artist_name is None:
			return self.track_name  # Return just the track name if artist is unknown
		else:
			return f"{self.track_name} by {self.artist_name}"  # Return 'track by artist' format if artist is known
