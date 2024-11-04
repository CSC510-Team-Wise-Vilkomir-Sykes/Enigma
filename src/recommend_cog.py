"""
recommend_cog.py

This module contains the RecommendCog class, a Discord bot cog for handling song recommendations
and polling based on user preferences. The cog includes two main commands:
- /poll: Allows users to select songs by reacting to a list of randomly chosen tracks from different genres.
- /recommend: Provides personalized song recommendations based on the user’s previous selections.

Classes:
    RecommendCog(commands.Cog): A cog that encapsulates song recommendation and polling commands.

Functions:
    - poll(ctx): Presents a list of 10 songs to the user, allowing them to choose up to 3 for recommendations.
    - recommend(ctx): Provides song recommendations based on selected songs, with options to save or request new suggestions.
    - generate_recommendations(selected_songs): Generates up to 10 song recommendations based on the genres of selected songs.

Dependencies:
    - discord.py: For creating and managing bot commands and message interactions.
    - asyncio: For handling asynchronous events like reactions.
    - pandas: For managing song data in DataFrames.
    - BotState: A module to maintain the current state of selected songs across bot sessions.
    - utils: Helper functions, including random_25 for selecting random recommendations.

Usage:
    Add this cog to your Discord bot instance to provide music recommendation features.
    Example:
        bot.add_cog(RecommendCog(bot))

Notes:
    This module assumes the presence of a "Song" class, which encapsulates track metadata (track name, artist, genre),
    and the "get_all_songs" and "get_songs_by_genre" functions to fetch songs.
"""

import discord
from discord.ext import commands

import random
import asyncio
from src.bot_state import BotState
from src.get_all import get_all_songs
from src.utils import random_25
from src.get_all import get_songs_by_genre
import pandas as pd
from src.song import Song


class RecommendCog(commands.Cog):
    """
        A Discord bot cog for song recommendation and polling features.
        Provides commands for polling songs by genre and recommending songs
        based on user-selected tracks.
    """
    def __init__(self, bot):
        self.bot = bot  # Storing the bot instance in the cog

    @commands.command(name="poll", help="Poll for recommendation")
    async def poll(self, ctx):
        """
            Poll command to display a list of 10 randomly selected songs from different genres.
            Allows the user to select up to 3 songs by reacting to message emojis.

            Parameters:
            - ctx (commands.Context): The context of the command invocation.
        """

        number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
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
                        artist_name=ten_random_songs.iloc[emoji_index]["artist_name"],
                        genre=ten_random_songs.iloc[emoji_index]["genre"],
                    )
                selected_songs.append(song)

                # Confirm addition with an embedded message
                favorite_embed = discord.Embed(
                    title="Added to Favorites",
                    description=f"{song.track_name} by {song.artist_name} ({song.genre})",
                    color=0x00FF00,
                )
                await ctx.send(embed=favorite_embed)
                # Update the song queue in BotState
                BotState.song_queue = selected_songs.copy()
            except asyncio.TimeoutError:
                break # End poll if user times out

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

    """
    This function displays a recommended song list, and allows user to queue recommended songs or get new recommendations
    """

    @commands.command(
        name="recommend", help="Handle recommendations based on selected songs"
    )
    async def recommend(self, ctx):
        """
            Recommend command to suggest songs based on previously selected tracks.
            Users can react to add songs to their queue, or get a new set of recommendations.

            Parameters:
            - ctx (commands.Context): The context of the command invocation.
        """
        if not BotState.song_queue:
            await ctx.send(
                embed=discord.Embed(
                    title="No Songs Selected",
                    description="Use /poll to select some songs first.",
                    color=0xFF0000,
                )
            )
            return

        number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
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
            f"{number_emojis[i]} {song.track_name} by {song.artist_name} ({song.genre})"
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
                            f"{number_emojis[i]} {song}"
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
                                title="Ending recommendation session",
                                description="Use /recommend command for music recommendation",
                                color=0xFF0000,
                            )
                        )
                        break
                else:
                    # Add selected song to the queue
                    index = number_emojis.index(str(reaction.emoji))
                    song = recommended_songs[index]
                    BotState.song_queue.append(song)
                    await ctx.send(
                        embed=discord.Embed(
                            title="Song Added",
                            description=f"Added {recommended_songs[index]}",
                            color=0x00FF00,
                        )
                    )

            except asyncio.TimeoutError:
                await ctx.send("Timeout occurred. No response received.")
                break

    def generate_recommendations(self, selected_songs):
        """
            Helper function that generates up to 10 recommended songs based on the genres of selected songs.

            Parameters:
            - selected_songs (list[Song]): A list of songs selected by the user.

            Returns:
            - list[Song]: A list of recommended Song objects.
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

        # Filter songs that match the genres collected and are not by the same artists as the input songs
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

        # Iterate through the matched songs and add them to recommendations if they meet the criteria
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
        Helper function for registering command cogs.

        Parameters:
            - client: The discord client to register this cog under.
        """
        await client.add_cog(RecommendCog(client))
