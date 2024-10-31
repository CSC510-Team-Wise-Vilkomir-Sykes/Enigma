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
	This function displays a recommended song list, and allows user to queue recommended songs or get new recommendations
	"""
	@commands.command(name='recommend', help='Handle recommendations based on selected songs')
	async def recommend(self, ctx):
		if not BotState.song_queue:
			await ctx.send(embed=discord.Embed(title="No Songs Selected", description="Use /poll to select some songs first.", color=0xff0000))
			return

		number_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
		control_emojis = {'🆕': 'new', '⏹️': 'stop'}

		while True:
			recommended_songs = self.generate_recommendations(BotState.song_queue)
			if not recommended_songs:
				await ctx.send(embed=discord.Embed(title="No Recommendations Found", description="Try different selections.", color=0xff0000))
				return

			description = "\n".join(f"{number_emojis[i]} {song}" for i, song in enumerate(recommended_songs))
			embed = discord.Embed(title="Recommended Songs", description=description, color=0x00ff00)
			msg = await ctx.send(embed=embed)

			for emoji in number_emojis[:len(recommended_songs)] + list(control_emojis.keys()):
				await msg.add_reaction(emoji)

			def check(reaction, user):
				return user == ctx.author and reaction.message.id == msg.id and (str(reaction.emoji) in number_emojis[:len(recommended_songs)] + list(control_emojis.keys()))

			try:
				reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
				if str(reaction.emoji) in control_emojis:
					action = control_emojis[str(reaction.emoji)]
					if action == 'new':
						continue
					elif action == 'stop':
						break
				else:
					# Add selected song to the queue
					index = number_emojis.index(str(reaction.emoji))
					BotState.song_queue.append(recommended_songs[index])
					await ctx.send(embed=discord.Embed(title="Song Added", description=f"Added {recommended_songs[index]}", color=0x00ff00))
					break
			except asyncio.TimeoutError:
				await ctx.send(embed=discord.Embed(title="Timeout", description="No response received.", color=0xff0000))
				break

	"""
	Helper function returns 10 recommended songs based on the songs that the user selected.
	"""	
	def generate_recommendations(self, selected_songs):
		recommendations = []
		seen_artists = {}  # Dictionary to track the number of songs recommended per artist

		# Aggregate genres from all selected songs
		genres = {song['genre'] for song in selected_songs}

		# Set a limit on how many times an artist can appear in the recommendations
		artist_limit = 2

		# Filter songs that match the genres collected and are not by the same artists as the input songs
		matched_songs = self.all_songs[
			self.all_songs['genre'].isin(genres) &
			(~self.all_songs['artist_name'].isin([song['artist_name'] for song in selected_songs])) &
			(~self.all_songs['track_name'].isin([song['track_name'] for song in selected_songs]))
		].copy()

		# Shuffle the matched songs to prevent bias
		matched_songs = matched_songs.sample(frac=1).reset_index(drop=True)

		# Iterate through the matched songs and add them to recommendations if they meet the criteria
		for _, matched_song in matched_songs.iterrows():
			song_info = f"{matched_song['track_name']} by {matched_song['artist_name']} ({matched_song['genre']})"
			artist_count = seen_artists.get(matched_song['artist_name'], 0)

			if song_info not in recommendations and artist_count < artist_limit:
				recommendations.append(song_info)
				seen_artists[matched_song['artist_name']] = artist_count + 1

			if len(recommendations) >= 10:
				break

		return recommendations[:10]  # Limit to 10 recommendations
	
	@staticmethod
	async def setup(client):
		await client.add_cog(RecommendCog(client))
