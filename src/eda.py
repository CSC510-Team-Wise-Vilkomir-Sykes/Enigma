import sqlite3
import pandas as pd


def get_top_songs(conn):
    query = "SELECT title, artist, chart_name FROM songs WHERE rank = 1 ORDER BY weeks_on_chart DESC LIMIT 10"
    df = pd.read_sql(query, conn)
    return df


def get_top_artists(conn):
	query = "SELECT artist, COUNT(*) as count FROM songs GROUP BY artist ORDER BY count DESC LIMIT 10"
	df = pd.read_sql(query, conn)
	return df

