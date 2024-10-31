import discord
from discord.ext import commands
import random
import asyncio
from src.bot_state import BotState
from src.get_all import get_all_songs
from src.utils import random_25
from src.get_all import get_songs_by_genre


class RecommendCog(commands.Cog):
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
		for index, (track_name, artist, genre) in enumerate(zip(ten_random_songs["track_name"], ten_random_songs["artist"], ten_random_songs["genre"]), start=1):
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
					selected_songs.append(ten_random_songs.iloc[emoji_index]["track_name"])
					await ctx.send(f"Added to favorites: {ten_random_songs.iloc[emoji_index]['track_name']} by {ten_random_songs.iloc[emoji_index]['artist']} ({ten_random_songs.iloc[emoji_index]['genre']})")
			except asyncio.TimeoutError:
				break

		if selected_songs:
			bot_message = "Selected songs are: " + ' , '.join(selected_songs)
			await ctx.send(bot_message)
			recommended_songs = self.recommend(selected_songs)
			BotState.song_queue = recommended_songs
		else:
			await ctx.send("No songs were selected.")

	"""
	This function returns recommended songs based on the songs that the user selected.
	"""
	@staticmethod
	def recommend(self, input_songs):
		# removing all songs with count = 1
		songs = get_all_songs()
		songs = songs.groupby('genre').filter(lambda x: len(x) > 0)
		# creating dictionary of song track_names and genre
		playlist = dict(zip(songs['track_name'], songs['genre']))
		# creating dictionary to count the frequency of each genre
		freq = {}
		for item in songs['genre']:
			if (item in freq):
				freq[item] += 1
			else:
				freq[item] = 1
		# create list of all songs from the input genre
		selected_list = []
		output = []
		for input in input_songs:
			if input in playlist.keys():
				for key, value in playlist.items():
					if playlist[input] == value:
						selected_list.append(key)
				selected_list.remove(input)
		if (len(selected_list) >= 10):
			output = random.sample(selected_list, 10)
		else:
			extra_songs = 10 - len(selected_list)
			song_names = songs['track_name'].to_list()
			song_names_filtered = [x for x in song_names if x not in selected_list]
			selected_list.extend(random.sample(song_names_filtered, extra_songs))
			output = selected_list.copy()
			return output

	@staticmethod
	async def setup(client):
		await client.add_cog(RecommendCog(client))
