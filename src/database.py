import sqlite3


def create_connection(db_file="songs.db"):
	conn = sqlite3.connect(db_file)
	return conn


def create_table():
	conn = create_connection()
	cursor = conn.cursor()
	cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chart_name TEXT,
            rank INTEGER,
            title TEXT,
            artist TEXT,
            weeks_on_chart INTEGER
        )
    ''')
	conn.commit()
	conn.close()


def insert_song(data):
	conn = create_connection()
	cursor = conn.cursor()
	cursor.execute('''
        INSERT INTO songs (chart_name, rank, title, artist, weeks_on_chart)
        VALUES (?, ?, ?, ?, ?)
    ''', (data['chart_name'], data['rank'], data['title'], data['artist'],
		  data.get('weeks_on_chart', None)))
	conn.commit()
	conn.close()


def clear_data():
	conn = create_connection()
	cursor = conn.cursor()
	cursor.execute('DELETE FROM songs')
	conn.commit()
	conn.close()
