import sqlite3

conn = sqlite3.connect('data/site.db')
cur = conn.cursor()
cur.execute('CREATE TABLE cards(oracle_id PRIMARY KEY, name, url, small, normal, large)')