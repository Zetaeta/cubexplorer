import json
from util.db import connect
import uuid


def get_cards():
    file = open('data/oracle-cards.json',"r")
    cards = json.load(file)
    conn = connect('data/site.db')
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
        return (uuid.UUID(id), name, uri, images['small'], images['normal'], images['large'],uuid.UUID(id))


    data = map(entry, cards)

    cur.executemany('INSERT OR REPLACE INTO cards (id, name, url, image_small, image_normal, image_large, used) VALUES (?, ?, ?, ?, ?, ?, COALESCE((SELECT used FROM Cards WHERE id = ?), 0))', data)
    conn.commit()

if __name__ == "__main__":
    get_cards()