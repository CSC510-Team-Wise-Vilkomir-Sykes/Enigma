import sqlite3
import unittest
from src.database import create_connection, create_table, insert_song, clear_data

class TestDatabase(unittest.TestCase):

    def test_connection(self):
        conn = create_connection("test_songs.db")
        self.assertIsNotNone(conn)


    def test_create_table(self):
        create_table("test_songs.db")
        conn = create_connection("test_songs.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='songs';")
        self.assertIsNotNone(cursor.fetchone())

    def test_insert_song(self):
        song_data = {
            'chart_name': 'Chart 1',
            'rank': 1,
            'title': 'Song 1',
            'artist': 'Artist 1',
            'weeks_on_chart': 10
        }
        insert_song(song_data, "test_songs.db")
        conn = create_connection("test_songs.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM songs WHERE title='Song 1';")
        self.assertIsNotNone(cursor.fetchone())

    # def test_clear_data(self):
    #     song_data = {
    #         'chart_name': 'Chart 1',
    #         'rank': 1,
    #         'title': 'Song 1',
    #         'artist': 'Artist 1',
    #         'weeks_on_chart': 10
    #     }
    #     insert_song(song_data, "test_songs.db")
    #     clear_data("test_songs.db")
    #     conn = create_connection("test_songs.db")
    #     cursor = conn.cursor()
    #     cursor.execute("SELECT * FROM songs;")
    #     self.assertIsNone(cursor.fetchone())

if __name__ == '__main__':
    unittest.main()