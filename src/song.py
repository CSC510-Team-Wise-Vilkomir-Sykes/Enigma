"""
song.py

What:
    The `song` module defines the `Song` class, a fundamental building block for representing individual music tracks within the application. Each `Song` instance encapsulates essential metadata, including the track name, artist name, and genre, enabling seamless integration with other components such as recommendation systems and user interfaces.

Why:
    In any music-related application, having a robust and flexible representation of songs is crucial. The `Song` class provides a standardized way to manage and manipulate song data, facilitating features like personalized recommendations, playlist creation, and genre-based filtering. By abstracting song details into a dedicated class, the module ensures consistency, scalability, and ease of maintenance across the codebase.

How:
    - **Creating a Song Instance**: Instantiate the `Song` class by providing the track name, and optionally, the artist name and genre. This creates a song object that can be used throughout the application.

    - **String Representation**: Utilize the `__str__` method to obtain a human-readable representation of the song, which is particularly useful for displaying song information in user interfaces or logs.

    - **Integration with Other Modules**: The `Song` class can be integrated with modules responsible for fetching song data, generating recommendations, or managing user playlists, ensuring a cohesive and interconnected system.

Example Use Cases:
    1. **Recommendation Systems**: Utilize `Song` instances to generate and display personalized song recommendations based on user preferences and listening history.

    2. **Playlist Management**: Allow users to create, modify, and view playlists composed of `Song` objects, enabling a personalized listening experience.

    3. **Music Browsing**: Facilitate browsing and searching of songs by various attributes such as genre, artist, or track name, leveraging the structured data provided by the `Song` class.

Classes:
    Song:
        Represents a music track with its associated details, including track name, artist name, and genre.

Functions:
    - __init__(track_name, artist_name=None, genre=None):
        Initializes a new instance of the `Song` class with the provided track name, artist name, and genre.

    - __str__():
        Returns a formatted string representation of the song, suitable for display purposes.

Dependencies:
    - None. The `Song` class is a standalone component that does not rely on external libraries or modules.

Usage:
    To create a new song instance, instantiate the `Song` class with the necessary details. This instance can then be used in various parts of the application, such as adding to playlists or generating recommendations.

    Example:
        ```python
        from song import Song

        # Creating a song with all details
        song1 = Song(track_name="Imagine", artist_name="John Lennon", genre="Rock")

        # Creating a song with only track name
        song2 = Song(track_name="Bohemian Rhapsody")

        print(song1)  # Output: Imagine by John Lennon
        print(song2)  # Output: Bohemian Rhapsody
        ```

Notes:
    - The `Song` class is designed to be simple and intuitive, ensuring ease of use and integration.
    - While the `artist_name` and `genre` attributes are optional, providing them enhances the functionality and applicability of the `Song` instances within the application.
    - Future extensions of the `Song` class can include additional metadata such as album name, release date, duration, and more, depending on the requirements of the application.

"""

class Song:
    """
    What:
        The `Song` class represents an individual music track, encapsulating its essential details such as the track name, artist name, and genre. It serves as a blueprint for creating song objects that can be utilized throughout the application for various functionalities like recommendations, playlist management, and display purposes.

    Why:
        A structured representation of songs is vital for any music-centric application. By defining a `Song` class, the module ensures that each song's data is consistently managed and easily accessible. This abstraction simplifies interactions with song data, enabling efficient processing, filtering, and display operations, thereby enhancing the overall functionality and user experience of the application.

    How:
        - **Initialization**: Create a `Song` instance by providing the track name, with optional parameters for artist name and genre. This allows for flexibility in representing songs with varying levels of detail.

        - **String Representation**: The `__str__` method provides a readable string format of the song, which can be used for displaying song information in user interfaces or logs.

        - **Integration**: `Song` instances can be integrated with other components such as databases, recommendation engines, and user interfaces, facilitating seamless data flow and interaction within the application.
    """

    def __init__(self, track_name, artist_name=None, genre=None, url=None):
        """
        What:
            Initializes a new instance of the `Song` class with the specified track name, and optionally, the artist name and genre.

        Why:
            Establishing a `Song` object with the necessary attributes ensures that each song's data is encapsulated in a consistent and accessible manner. This setup is essential for functionalities that depend on song metadata, such as generating recommendations, creating playlists, and displaying song information.

        How:
            - **track_name (str)**: Mandatory parameter representing the name of the song.
            - **artist_name (str, optional)**: Optional parameter for the artist's name. Defaults to `None` if not provided.
            - **genre (str, optional)**: Optional parameter for the song's genre. Defaults to `None` if not provided.

        Example:
            ```python
            # Creating a song with all details
            song = Song(track_name="Shape of You", artist_name="Ed Sheeran", genre="Pop")

            # Creating a song with only track name
            song = Song(track_name="Unknown Song")
            ```

        Args:
            track_name (str): The name of the song.
            artist_name (str, optional): The name of the artist. Defaults to None if unknown.
            genre (str, optional): The genre of the song. Defaults to None if unspecified.
        """
        self.track_name = track_name  # The title of the song
        self.artist_name = artist_name  # The artist who performed the song
        self.genre = genre  # The genre of the song
        self.url = url # The URL of the song retrieved from YouTube

    def __str__(self):
        """
        What:
            Provides a human-readable string representation of the `Song` instance, formatted to include both the track name and the artist name if available.

        Why:
            A clear and concise string representation is essential for displaying song information in user interfaces, logs, and other outputs. It enhances readability and ensures that users can easily identify and differentiate between songs.

        How:
            - If the `artist_name` attribute is provided, the method returns a string in the format "`<track_name> by <artist_name>`".
            - If the `artist_name` is not provided (`None`), it returns just the `track_name`.

        Example:
            ```python
            song_with_artist = Song(track_name="Yesterday", artist_name="The Beatles")
            print(song_with_artist)  # Output: Yesterday by The Beatles

            song_without_artist = Song(track_name="Unknown Track")
            print(song_without_artist)  # Output: Unknown Track
            ```

        Returns:
            str: The string representation of the song.
        """
        if self.artist_name is None:
            return self.track_name  # Return just the track name if artist is unknown
        else:
            # Return 'track by artist' format if artist is known
            return f"{self.track_name} by {self.artist_name}"
