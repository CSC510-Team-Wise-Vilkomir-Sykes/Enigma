import unittest
import sqlite3
import pandas as pd
from src.eda import get_top_songs, get_top_artists, get_longest_charting_songs


class TestEDA(unittest.TestCase):

	def setUp(self):
		self.conn = sqlite3.connect(':memory:')
		self.create_test_data()

	def tearDown(self):
		self.conn.close()

	def create_test_data(self):
		cursor = self.conn.cursor()
		cursor.execute('''
            CREATE TABLE songs (
                title TEXT,
                artist TEXT,
                chart_name TEXT,
                rank INTEGER,
                weeks_on_chart INTEGER
            )
        ''')
		cursor.executemany('''
            INSERT INTO songs (title, artist, chart_name, rank, weeks_on_chart)
            VALUES (?, ?, ?, ?, ?)
        ''', [
			('Song1', 'Artist1', 'Chart1', 1, 20),
			('Song2', 'Artist2', 'Chart2', 1, 15),
			('Song3', 'Artist3', 'Chart3', 1, 10),
			('Song4', 'Artist1', 'Chart4', 1, 25),
			('Song5', 'Artist2', 'Chart5', 1, 30),
			('Song6', 'Artist4', 'Chart6', 1, 5),
			('Song7', 'Artist5', 'Chart7', 1, 8),
			('Song8', 'Artist6', 'Chart8', 1, 12),
			('Song9', 'Artist7', 'Chart9', 1, 18),
			('Song10', 'Artist8', 'Chart10', 1, 22),
			('Song11', 'Artist9', 'Chart11', 1, 35),
			('Song12', 'Artist10', 'Chart12', 1, 40)
		])
		self.conn.commit()

	def test_get_top_songs(self):
		"""Test that get_top_songs returns the top 10 songs by weeks on chart."""
		df = get_top_songs(self.conn)
		self.assertEqual(len(df), 10)
		self.assertEqual(df.iloc[0]['title'], 'Song12')

	def test_get_top_artists(self):
		"""Test that get_top_artists returns the top 10 artists by number of songs."""
		df = get_top_artists(self.conn)
		self.assertEqual(len(df), 10)
		self.assertEqual(df.iloc[0]['artist'], 'Artist2')

	def test_get_longest_charting_songs(self):
		"""Test that get_longest_charting_songs returns the top 10 songs by weeks on chart."""
		df = get_longest_charting_songs(self.conn)
		self.assertEqual(len(df), 10)
		self.assertEqual(df.iloc[0]['title'], 'Song12')

	def test_get_top_songs_empty(self):
		"""Test that get_top_songs returns an empty DataFrame when there are no songs."""
		cursor = self.conn.cursor()
		cursor.execute('DELETE FROM songs')
		self.conn.commit()
		df = get_top_songs(self.conn)
		self.assertTrue(df.empty)

	def test_get_top_artists_empty(self):
		"""Test that get_top_artists returns an empty DataFrame when there are no songs."""
		cursor = self.conn.cursor()
		cursor.execute('DELETE FROM songs')
		self.conn.commit()
		df = get_top_artists(self.conn)
		self.assertTrue(df.empty)

	def test_get_longest_charting_songs_empty(self):
		"""Test that get_longest_charting_songs returns an empty
		DataFrame when there are no songs."""
		cursor = self.conn.cursor()
		cursor.execute('DELETE FROM songs')
		self.conn.commit()
		df = get_longest_charting_songs(self.conn)
		self.assertTrue(df.empty)

	def test_get_top_songs_no_rank_1(self):
		"""Test that get_top_songs returns an empty DataFrame when no songs have rank 1."""
		cursor = self.conn.cursor()
		cursor.execute('UPDATE songs SET rank = 2 WHERE rank = 1')
		self.conn.commit()
		df = get_top_songs(self.conn)
		self.assertTrue(df.empty)

	def test_get_top_artists_no_songs(self):
		"""Test that get_top_artists does not include an artist with no songs."""
		cursor = self.conn.cursor()
		cursor.execute('DELETE FROM songs WHERE artist = "Artist1"')
		self.conn.commit()
		df = get_top_artists(self.conn)
		self.assertNotIn('Artist1', df['artist'].values)

	def test_get_longest_charting_songs_no_weeks(self):
		"""Test that get_longest_charting_songs returns an empty DataFrame when all songs have 0
		weeks on chart."""
		cursor = self.conn.cursor()
		cursor.execute('UPDATE songs SET weeks_on_chart = 0')
		self.conn.commit()
		df = get_longest_charting_songs(self.conn)
		self.assertTrue(df.empty)

	def test_get_top_songs_multiple_charts(self):
		"""Test that get_top_songs returns the top 10 songs when there are multiple charts."""
		cursor = self.conn.cursor()
		cursor.execute('''
            INSERT INTO songs (title, artist, chart_name, rank, weeks_on_chart)
            VALUES ("Song13", "Artist11", "Chart13", 1, 45)
        ''')
		self.conn.commit()
		df = get_top_songs(self.conn)
		self.assertEqual(len(df), 10)
		self.assertIn('Song13', df['title'].values)



if __name__ == '__main__':
	unittest.main()
