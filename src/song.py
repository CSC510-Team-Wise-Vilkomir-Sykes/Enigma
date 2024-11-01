class Song:
	def __init__(self, track_name, artist_name=None, genre=None):
		self.track_name = track_name
		self.artist_name = artist_name
		self.genre = genre

	def __str__(self):
		if self.artist_name is None:
			return self.track_name
		else:
			return f"{self.track_name} by {self.artist_name}"
