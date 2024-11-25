"""
recommend_cog.py

What:
    The `recommend_cog` module introduces the `RecommendCog` class, a Discord bot cog tailored for song recommendations and polling based on user preferences. It facilitates interactive commands that allow users to participate in song selection polls and receive personalized music recommendations, enhancing the musical engagement within a Discord server.

Why:
    In the vibrant environment of Discord communities, music plays a pivotal role in fostering engagement and camaraderie. The `RecommendCog` empowers users to collaboratively curate playlists, discover new genres, and personalize their listening experience. By leveraging user interactions and preferences, it creates a dynamic and responsive music recommendation system that keeps the community lively and engaged.

How:
    - **/poll Command**: Users invoke the `/poll` command to initiate a poll where they are presented with a list of 10 randomly selected songs spanning various genres. Each song is associated with a unique emoji. Users can react to the message with the corresponding emojis to select up to 3 songs they prefer. These selections are then used to tailor future recommendations.

    - **/recommend Command**: Based on the songs selected through the `/poll` command, users can invoke the `/recommend` command to receive personalized song suggestions. The bot generates a list of recommended songs that align with the genres of the user's favorites. Users can interact with these recommendations by adding songs to their queue or requesting a new set of suggestions, ensuring a continuously evolving and personalized music experience.

    Example Use Cases:
        1. **Community Playlist Building**: Facilitate the creation of a community-driven playlist where members can vote on their favorite songs, ensuring the playlist reflects the collective taste of the group.
        2. **Music Discovery**: Help users explore new music by recommending tracks that align with their existing preferences, broadening their musical horizons.
        3. **Event Hosting**: Enhance virtual events or game nights with curated music selections that keep participants engaged and entertained.

Classes:
    RecommendCog(commands.Cog):
        Encapsulates the song recommendation and polling commands, managing user interactions, song selections, and the generation of personalized recommendations.

Functions:
    - poll(ctx):
        Initiates a song selection poll where users can choose their preferred songs by reacting with emojis. Facilitates up to 3 song selections to personalize future recommendations.

    - recommend(ctx):
        Generates and presents personalized song recommendations based on the user's previous selections from the poll. Allows users to add recommended songs to their queue or request new recommendations.

    - generate_recommendations(selected_songs):
        Processes the user's selected songs to generate a tailored list of up to 10 song recommendations, focusing on the genres of the chosen tracks while ensuring diversity in artists.

Dependencies:
    - discord.py: For creating and managing bot commands, handling message interactions, and managing embeds and reactions.
    - asyncio: For managing asynchronous events, particularly waiting for user reactions in real-time.
    - pandas: For efficient management and manipulation of song data within DataFrames.
    - BotState: A custom module to maintain the current state of selected songs across different bot sessions and commands.
    - utils: Contains helper functions, including `random_25` for selecting random song recommendations.

Usage:
    To integrate the `RecommendCog` into your Discord bot, add it to your bot instance as shown below. This will enable the polling and recommendation features within your Discord server.

    Example:
        ```python
        from recommend_cog import RecommendCog

        bot = commands.Bot(command_prefix="/")
        bot.add_cog(RecommendCog(bot))
        bot.run('YOUR_BOT_TOKEN')
        ```

Notes:
    - The module assumes the existence of a `Song` class, which encapsulates essential track metadata such as track name, artist, and genre.
    - It relies on the `get_all_songs` and `get_songs_by_genre` functions to fetch and filter songs from the dataset.
    - Ensure that the dependencies (`discord.py`, `asyncio`, `pandas`, `BotState`, and `utils`) are correctly installed and configured in your project environment.

"""

import discord
from discord.ext import commands

import random
import asyncio
from src.bot_state import BotState
from src.get_all import get_all_songs
from src.get_all import get_songs_by_genre
from src.song import Song


class RecommendCog(commands.Cog):
    """
    What:
        The `RecommendCog` is a Discord bot cog designed to facilitate song recommendations and polling based on user interactions. It provides commands that allow users to participate in song selection polls and receive personalized music recommendations.

    Why:
        By enabling users to actively select and receive tailored song suggestions, the cog enhances user engagement and promotes a more interactive and enjoyable musical experience within the Discord server.

    How:
        - **poll Command**: Initiates a poll where users can select their favorite songs from a randomly generated list by reacting with specific emojis.
        - **recommend Command**: Generates and presents song recommendations based on the user's previous selections from the poll, allowing further interaction such as adding songs to a queue or requesting new recommendations.
    """

    def __init__(self, bot):
        """
        Initializes the RecommendCog with the Discord bot instance.

        Parameters:
            bot (commands.Bot): The Discord bot instance to which this cog is being added.
        """
        self.bot = bot  # Storing the bot instance in the cog

    @commands.command(name="poll", help="Initiate a song selection poll for personalized recommendations")
    async def poll(self, ctx):
        """
        What:
            The `/poll` command presents users with a list of 10 randomly selected songs from various genres. Users can select up to 3 songs they prefer by reacting with corresponding emojis.

        Why:
            This interactive poll allows the bot to gather user preferences, which are essential for generating personalized song recommendations that align with the user's taste.

        How:
            - Sends a message prompting users to react with number emojis corresponding to their favorite songs.
            - Displays a list of 10 songs with associated emojis.
            - Waits for the user to react to the message, capturing up to 3 song selections.
            - Confirms each selection and updates the bot's state with the chosen songs.

        Example:
            A user types `/poll` in the Discord channel. The bot responds with a list of 10 songs, each numbered from 1️⃣ to 🔟. The user reacts with 1️⃣, 3️⃣, and 5️⃣ to select their top 3 songs, which are then used for personalized recommendations.

        Parameters:
            ctx (commands.Context): The context of the command invocation, containing information like the channel, author, and guild.
        """
        number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣",
                         "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        selected_songs = []
        bot_message = "React with the numbers to the songs you like. You can select up to 3 songs."
        await ctx.send(bot_message)

        # Fetch 10 random songs by genre
        ten_random_songs = get_songs_by_genre(10)

        # Create and display a list of song names with corresponding emojis
        song_list_message = ""
        for index, (track_name, artist, genre) in enumerate(
            zip(
                ten_random_songs["track_name"],
                ten_random_songs["artist_name"],
                ten_random_songs["genre"],
            ),
            start=1,
        ):
            song_list_message += (
                f"{number_emojis[index-1]} - {track_name} by {artist} ({genre})\n"
            )

        poll_embed = discord.Embed(
            title="Song Selection", description=song_list_message, color=0x31FF00
        )
        react_message = await ctx.send(embed=poll_embed)

        # Add reaction emojis for each song
        for emoji in number_emojis[: len(ten_random_songs)]:
            await react_message.add_reaction(emoji)

        # Check function to validate reactions
        def check(reaction, user):
            return (
                user == ctx.author
                and reaction.message.id == react_message.id
                and str(reaction.emoji) in number_emojis
            )

        # Collect up to 3 song selections from user reactions
        while len(selected_songs) < 3:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=60.0, check=check
                )
                emoji_index = number_emojis.index(str(reaction.emoji))

                # Check if song is already selected, to avoid duplicates
                if emoji_index < len(ten_random_songs) and ten_random_songs.iloc[
                    emoji_index
                ]["track_name"] not in [song.track_name for song in selected_songs]:
                    song = Song(
                        track_name=ten_random_songs.iloc[emoji_index]["track_name"],
                        artist_name=ten_random_songs.iloc[emoji_index][
                            "artist_name"],
                        genre=ten_random_songs.iloc[emoji_index]["genre"],
                    )
                    selected_songs.append(song)

                    # Confirm addition with an embedded message
                    favorite_embed = discord.Embed(
                        title="Added to Favorites",
                        description=f"{song.track_name} by {song.artist_name} " +
                                f"({song.genre})",
                        color=0x00FF00,
                    )
                    await ctx.send(embed=favorite_embed)
                    # Update the song queue in BotState
                    BotState.song_queue = selected_songs.copy()
            except asyncio.TimeoutError:
                break  # End poll if user times out

        # Send a summary of selected songs or notify if none were selected
        if selected_songs:
            summary_embed = discord.Embed(
                title="Selected Songs",
                description=" , ".join([song.track_name for song in selected_songs]),
                color=0x31FF00,
            )
            await ctx.send(embed=summary_embed)
        else:
            await ctx.send("No songs were selected.")

    @commands.command(
        name="recommend", help="Get personalized song recommendations based on your selections"
    )
    async def recommend(self, ctx):
        """
        What:
            The `/recommend` command generates and displays a list of personalized song recommendations based on the user's previously selected songs from the poll. It allows users to interact with the recommendations by adding songs to their queue or requesting new sets of suggestions.

        Why:
            By providing tailored recommendations, the bot enhances the user's music discovery experience, ensuring that suggested songs align with their established preferences and encouraging continued engagement.

        How:
            - Checks if the user has any previously selected songs. If not, prompts the user to use the `/poll` command first.
            - Generates a list of recommended songs based on the genres of the selected songs.
            - Sends an embedded message displaying the recommended songs with corresponding emojis.
            - Adds reaction emojis for each recommended song and control options (e.g., requesting new recommendations or stopping the session).
            - Listens for user reactions to either add a song to the queue, request new recommendations, or end the recommendation session.

        Example:
            After selecting favorite songs using `/poll`, a user invokes `/recommend`. The bot responds with a list of recommended songs. The user reacts with the emoji corresponding to a song to add it to their queue or with 🆕 to get a fresh set of
            recommendations.

        Parameters:
            ctx (commands.Context): The context of the command invocation, containing information like the channel, author, and guild.
        """
        if not BotState.song_queue:
            await ctx.send(
                embed=discord.Embed(
                    title="No Songs Selected",
                    description="Use `/poll` to select some songs first.",
                    color=0xFF0000,
                )
            )
            return

        number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣",
                         "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        control_emojis = {"🆕": "new", "⏹️": "stop"}

        # Generate initial recommendations
        recommended_songs = self.generate_recommendations(BotState.song_queue)
        if not recommended_songs:
            await ctx.send(
                embed=discord.Embed(
                    title="No Recommendations Found",
                    description="Try different selections.",
                    color=0xFF0000,
                )
            )
            return

        # Display recommended songs
        description = "\n".join(
            f"{number_emojis[i]} {song.track_name} by {song.artist_name} ("
            f"{song.genre})"
            for i, song in enumerate(recommended_songs)
        )
        embed = discord.Embed(
            title="Recommended Songs", description=description, color=0x00FF00
        )
        msg = await ctx.send(embed=embed)

        # Add reactions for songs and controls (new recommendations or stop)
        for emoji in number_emojis[: len(recommended_songs)] + list(
                control_emojis.keys()
        ):
            await msg.add_reaction(emoji)

        # Reaction-based interaction loop
        while True:

            # Check function to validate reactions
            def check(reaction, user):
                return (
                    user == ctx.author
                    and reaction.message.id == msg.id
                    and (
                        str(reaction.emoji)
                        in number_emojis[: len(recommended_songs)]
                        + list(control_emojis.keys())
                    )
                )

            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=300.0, check=check
                )
                if str(reaction.emoji) in control_emojis:
                    action = control_emojis[str(reaction.emoji)]
                    # Handle control actions: new recommendation or stop
                    if action == "new":
                        # Get a fresh set of recommendations
                        await msg.clear_reactions()
                        recommended_songs = self.generate_recommendations(
                            BotState.song_queue
                        )
                        if not recommended_songs:
                            await ctx.send("No further recommendations found.")
                            break
                        description = "\n".join(
                            f"{number_emojis[i]} {song.track_name} by {song.artist_name} ({song.genre})"
                            for i, song in enumerate(recommended_songs)
                        )
                        embed = discord.Embed(
                            title="New Recommended Songs",
                            description=description,
                            color=0x00FF00,
                        )
                        await msg.edit(embed=embed)
                        for emoji in number_emojis[: len(recommended_songs)] + list(
                            control_emojis.keys()
                        ):
                            await msg.add_reaction(emoji)
                    elif action == "stop":
                        # Stop the recommendation session
                        await ctx.send(
                            embed=discord.Embed(
                                title="Ending Recommendation Session",
                                description="Use `/recommend` command again for new recommendations.",
                                color=0xFF0000,
                            )
                        )
                        break
                else:
                    # Add selected song to the queue
                    index = number_emojis.index(str(reaction.emoji))
                    if index < len(recommended_songs):
                        song = recommended_songs[index]
                        if song not in BotState.song_queue:
                            BotState.song_queue.append(song)
                            await ctx.send(
                                embed=discord.Embed(
                                    title="Song Added",
                                    description=f"Added `{song.track_name}` by `{song.artist_name}` to your queue.",
                                    color=0x00FF00,
                                )
                            )
                        else:
                            await ctx.send(
                                embed=discord.Embed(
                                    title="Already in Queue",
                                    description=f"`{song.track_name}` is already in your queue.",
                                    color=0xFFFF00,
                                )
                            )
            except asyncio.TimeoutError:
                await ctx.send("Timeout occurred. No response received.")
                break

    def generate_recommendations(self, selected_songs):
        """
        What:
            Generates a list of up to 10 song recommendations based on the genres of the user's selected songs.

        Why:
            To provide users with personalized song suggestions that align with their musical preferences, enhancing their discovery of new tracks within their favored genres.

        How:
            - Aggregates the genres from the selected songs.
            - Filters all available songs to match these genres, excluding songs by the same artists or already selected tracks.
            - Shuffles the filtered list to ensure randomness and prevent bias.
            - Iterates through the shuffled list, adding songs to the recommendations while limiting the number of songs per artist to maintain diversity.
            - Returns the top 10 recommendations from the curated list.

        Parameters:
            selected_songs (list[Song]): A list of songs selected by the user through the poll.

        Returns:
            list[Song]: A list of up to 10 recommended `Song` objects tailored to the user's genre preferences.
        """
        recommendations = []
        seen_artists = (
            {}
        )  # Dictionary to track the number of songs recommended per artist

        # Fetch all songs dynamically
        all_songs = get_all_songs()

        # Aggregate genres from all selected songs
        genres = {song.genre for song in selected_songs}

        # Set a limit on how many times an artist can appear in the recommendations
        artist_limit = 2

        # Filter songs that match the genres collected and are not by the same
        # artists as the input songs
        matched_songs = all_songs[
            all_songs["genre"].isin(genres)
            & (
                ~all_songs["artist_name"].isin(
                    [song.artist_name for song in selected_songs]
                )
            )
            & (
                ~all_songs["track_name"].isin(
                    [song.track_name for song in selected_songs]
                )
            )
            ].copy()

        # Shuffle the matched songs to prevent bias
        matched_songs = matched_songs.sample(frac=1).reset_index(drop=True)

        # Iterate through the matched songs and add them to recommendations if
        # they meet the criteria
        for _, matched_song in matched_songs.iterrows():
            song = Song(
                track_name=matched_song["track_name"],
                artist_name=matched_song["artist_name"],
                genre=matched_song["genre"],
            )
            artist_count = seen_artists.get(song.artist_name, 0)

            if song not in recommendations and artist_count < artist_limit:
                recommendations.append(song)
                seen_artists[song.artist_name] = artist_count + 1

            if len(recommendations) >= 10:
                break

        return recommendations[:10]  # Limit to 10 recommendations

    @staticmethod
    async def setup(client):
        """
        What:
            Registers the `RecommendCog` with the Discord client.

        Why:
            To ensure that the bot recognizes and loads the cog, making its commands and functionalities available to users.

        How:
            - Adds an instance of `RecommendCog` to the provided Discord client.

        Parameters:
            client (discord.Client): The Discord client instance to which the cog will be added.
        """
        await client.add_cog(RecommendCog(client))
