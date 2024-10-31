import discord
from discord.ext import commands
import random
from src.bot_state import BotState
from src.get_all import get_all_songs
from src.utils import random_25


class RecommendCog(commands.Cog):
	"""
	    Function to generate poll for playing the recommendations
	"""

	@commands.command(name='poll', help='Poll for recommendation')
	async def poll(self, ctx):
		reactions = ['👍', '👎']
		selected_songs = []
		count = 0
		bot_message = "Select song preferences by reaction '👍' or '👎' to the choices. \nSelect 3 songs"
		await ctx.send(bot_message)
		ten_random_songs = random_25()
		for ele in zip(ten_random_songs["track_name"],
					   ten_random_songs["artist"]):
			bot_message = str(ele[0]) + " By " + str(ele[1])
			description = []
			poll_embed = discord.Embed(title=bot_message,
									   color=0x31FF00,
									   description=''.join(description))
			react_message = await ctx.send(embed=poll_embed)
			for reaction in reactions[:len(reactions)]:
				await react_message.add_reaction(reaction)
			res, user = await self.bot.wait_for('reaction_add')
			if (res.emoji == u'👍'):
				selected_songs.append(str(ele[0]))
				count += 1
			if (count == 3):
				bot_message = "Selected songs are : " + \
							  ' , '.join(selected_songs)
				await ctx.send(bot_message)
				break
		recommended_songs = self.recommend(selected_songs)
		BotState.song_queue = recommended_songs
		# await self.play_song(BotState.song_queue[0], ctx)
		# ^-- ignore this probably (all /poll needs to do is add songs to the queue

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
