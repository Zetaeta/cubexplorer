import json
import sqlite3

file = open('data/oracle-cards.json',"r")
cards = json.load(file)
conn = sqlite3.connect('data/site.db')
cur = conn.cursor()


def entry(card):
    id = card['oracle_id']
    name = card['name']
    uri =card['scryfall_uri']
    images = None
    if 'image_uris' not in card:
        print(card)
        card = card['card_faces'][0]
    images = card['image_uris']
    return (id, name, uri, images['small'], images['normal'], images['large'])


data = map(entry, cards)

cur.executemany('INSERT INTO cards VALUES (?, ?, ?, ?, ?, ?)', data)
conn.commit()
