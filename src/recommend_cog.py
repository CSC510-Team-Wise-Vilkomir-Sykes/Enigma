import discord
from discord.ext import commands

import random
import asyncio
from src.bot_state import BotState
from src.get_all import get_all_songs
from src.utils import random_25
from src.get_all import get_songs_by_genre
import pandas as pd


class RecommendCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot  # Storing the bot instance in the cog
		self.all_songs = pd.read_csv("./data/tcc_ceds_music.csv")

	"""
	Function to generate poll for playing the recommendations
	"""
	@commands.command(name='poll', help='Poll for recommendation')
	async def poll(self, ctx):
		number_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
		selected_songs = []
		bot_message = "React with the numbers to the songs you like. You can select up to 3 songs."
		await ctx.send(bot_message)
		
		# Fetch 10 songs from different genres
		ten_random_songs = get_songs_by_genre(10)
		
		# Display song name, artist, and genre
		song_list_message = ""
		for index, (track_name, artist, genre) in enumerate(zip(ten_random_songs["track_name"], ten_random_songs["artist_name"], ten_random_songs["genre"]), start=1):
			song_list_message += f"{number_emojis[index-1]} - {track_name} by {artist} ({genre})\n"
		
		poll_embed = discord.Embed(title="Song Selection", description=song_list_message, color=0x31FF00)
		react_message = await ctx.send(embed=poll_embed)
		
		# Add reactions for number emojis
		for emoji in number_emojis[:len(ten_random_songs)]:
			await react_message.add_reaction(emoji)

		# Collect reactions
		def check(reaction, user):
			return user == ctx.author and reaction.message.id == react_message.id and str(reaction.emoji) in number_emojis

		while len(selected_songs) < 3:
			try:
				reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
				emoji_index = number_emojis.index(str(reaction.emoji))
				if emoji_index < len(ten_random_songs) and ten_random_songs.iloc[emoji_index]["track_name"] not in selected_songs:
					song_info = {
                    'track_name': ten_random_songs.iloc[emoji_index]["track_name"],
                    'artist_name': ten_random_songs.iloc[emoji_index]["artist_name"],
                    'genre': ten_random_songs.iloc[emoji_index]["genre"]
                }
				selected_songs.append(song_info)
				favorite_embed = discord.Embed(
					title="Added to Favorites",
					description=f"{song_info['track_name']} by {song_info['artist_name']} ({song_info['genre']})",
					color=0x00FF00
				)
				await ctx.send(embed=favorite_embed)
			except asyncio.TimeoutError:
				break

		if selected_songs:
			BotState.song_queue = selected_songs.copy()
			summary_embed = discord.Embed(
				title="Selected Songs",
				description=" , ".join([song['track_name'] for song in selected_songs]),
				color=0x31FF00
			)
			await ctx.send(embed=summary_embed)
		else:
			await ctx.send("No songs were selected.")

	"""
	This function returns recommended songs based on the songs that the user selected.
	"""
	@commands.command(name='recommend', help='Handle recommendations based on selected songs')
	async def recommend(self, ctx):
		if not BotState.song_queue:
			no_songs_embed = discord.Embed(
				title="No Songs Selected",
				description="No songs have been selected yet. Use /poll to select some songs first.",
				color=0xff0000
			)
			await ctx.send(embed=no_songs_embed)
			return

		while True:  # Begin a loop to handle continuous interaction
			recommended_songs = self.generate_recommendations(BotState.song_queue)
			if not recommended_songs:
				no_recommendations_embed = discord.Embed(
					title="No Recommendations Found",
					description="Could not find any recommendations based on your chosen songs.",
					color=0xff0000
				)
				await ctx.send(embed=no_recommendations_embed)
				return

			recommendations_embed = discord.Embed(
				title="Recommended Songs",
				description="Based on your choices, I recommend these songs:\n" + "\n".join(recommended_songs),
				color=0x00ff00
			)
			await ctx.send(embed=recommendations_embed)

			decision_embed = discord.Embed(
				title="What's Next?",
				description="Would you like to add these songs to your queue or get a new list? \n\n Type 'add' to add, \n'new' for a new list, \nor 'stop' to end.",
				color=0x0000ff
			)
			await ctx.send(embed=decision_embed)

			def check(m):
				return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['add', 'new', 'stop']

			try:
				response = await self.bot.wait_for('message', timeout=60.0, check=check)
				if response.content.lower() == 'add':
					BotState.song_queue.extend(recommended_songs)
					added_embed = discord.Embed(
						title="Songs Added",
						description="Songs added to your queue.",
						color=0x00ff00
					)
					await ctx.send(embed=added_embed)
					break  # Exit the loop after adding songs
				elif response.content.lower() == 'new':
					BotState.song_queue = recommended_songs  # Optionally reset the queue or handle as desired
					continue  # Continue to generate new recommendations
				elif response.content.lower() == 'stop':
					break  # Exit the loop and end the interaction
			except asyncio.TimeoutError:
				timeout_embed = discord.Embed(
					title="Timeout",
					description="No response received. If you'd like to perform any actions, please use the command again.",
					color=0xff0000
				)
				await ctx.send(embed=timeout_embed)
				break  # Exit the loop on timeout


	def generate_recommendations(self, selected_songs):
        # Filter all songs to find matches based on the genre and artist of the selected songs
		recommendations = []
		for song in selected_songs:
			# Extract the genre and artist from the selected song
			genre, artist = song['genre'], song['artist_name']

			# Find other songs with the same genre and artist
			matched_songs = self.all_songs[
				(self.all_songs['genre'] == genre) & 
				(self.all_songs['artist_name'] == artist) &
				(~self.all_songs['track_name'].isin([song['track_name'] for song in selected_songs]))  # Exclude already selected songs
			]

			# Add found songs to recommendations, ensure no duplicates
			for idx, matched_song in matched_songs.iterrows():
				song_info = f"{matched_song['track_name']} by {matched_song['artist_name']} ({matched_song['genre']})"
				if song_info not in recommendations:
					recommendations.append(song_info)
			
			# Limit the number of recommendations if necessary
			if len(recommendations) >= 10:
				break

		return recommendations[:10]  # Return up to 10 recommendations
	
	@staticmethod
	async def setup(client):
		await client.add_cog(RecommendCog(client))
