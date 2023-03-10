import sqlite3
import redis
import uuid


def get_redis():
    return redis.Redis()


def connect(path):
    conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
    sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
    sqlite3.register_converter('UUID', lambda b: uuid.UUID(bytes_le=b))
    return conn


def create_card_db():
    conn = connect('data/site.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE cards(id UUID PRIMARY KEY, name TEXT, url TEXT, image_small TEXT, image_normal TEXT, image_large TEXT, used BOOLEAN DEFAULT 0)')
    pass
