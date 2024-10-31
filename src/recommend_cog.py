import discord
from discord.ext import commands
import random
import asyncio
from src.bot_state import BotState
from src.get_all import get_all_songs
from src.utils import random_25
from src.get_all import get_songs_by_genre


class RecommendCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot  # Storing the bot instance in the cog

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
	@commands.command(name='recommend', help='Handle recommendations based on selected songs')
	async def recommend(self, ctx):
		if not BotState.song_queue:
			await ctx.send("No songs have been selected yet. Use /poll to select some songs first.")
			print("Debug: Song queue in recommend -", BotState.song_queue)  # Debug output
			return
		
		# Displaying the chosen songs
		chosen_songs_message = "You have chosen the following songs:\n" + "\n".join(BotState.song_queue)
		await ctx.send(chosen_songs_message)
		
		# Generating recommendations based on the chosen songs
		recommended_songs = self.generate_recommendations(BotState.song_queue)
		if not recommended_songs:
			await ctx.send("Could not find any recommendations based on your chosen songs.")
			return
		
		recommendations_message = "Based on your choices, I recommend these songs:\n" + "\n".join(recommended_songs)
		await ctx.send(recommendations_message)
		
		# Asking the user for the next action
		decision_message = "Would you like to add these songs to your queue (Type 'add') or get a new list (Type 'new')?"
		await ctx.send(decision_message)
		
		# Check for user response
		def check(m):
			return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['add', 'new']
		
		try:
			response = await self.bot.wait_for('message', timeout=60.0, check=check)
			if response.content.lower() == 'add':
				BotState.song_queue.extend(recommended_songs)
				await ctx.send("Songs added to your queue.")
			elif response.content.lower() == 'new':
				BotState.song_queue = recommended_songs
				await ctx.send("Your queue has been updated with new songs.")
		except asyncio.TimeoutError:
			await ctx.send("No response received. If you'd like to perform any actions, please use the command again.")

	def generate_recommendations(self, selected_songs):
		# Assuming you have some logic to generate recommendations
		# This is a placeholder function that should contain your recommendation algorithm
		# For example, based on genre, popularity, etc.
		return ["Song 1", "Song 2", "Song 3"]  # Sample output

	@staticmethod
	async def setup(client):
		await client.add_cog(RecommendCog(client))
