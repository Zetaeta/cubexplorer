
import uuid, sqlite3
import os
import json
from collections import Counter


def connect(path):
    conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
    sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
    sqlite3.register_converter('UUID', lambda b: uuid.UUID(bytes_le=b))
    return conn


def create_incidence_db():
    db = connect('data/site.db')
    cur = db.cursor()
    cur.execute("""CREATE TABLE Incidence (
                        cube_id varchar(100),
                        card_id UUID,
                        mult DEFAULT 1,
                        PRIMARY KEY (cube_id, card_id))""")

def delete_incidence_db():
    db = connect('data/site.db')
    cur = db.cursor()
    cur.execute('DROP TABLE Incidence')

def populate_incidence_db(db=connect('data/site.db')):
    cur = db.cursor()
    def is_json(filename):
        # print(filename[-4:])
        return filename[-4:] == 'json'
    for cube_file in filter(is_json, os.listdir('data/cubes')):
        print(cube_file)
        file = open('data/cubes/' +cube_file, 'r')
        cube_data = json.load(file)
        cube_id = cube_data['shortID']
        for (card_id, mult) in Counter(cube_data['cardOracles']).items():
            cur.execute('INSERT OR REPLACE INTO Incidence (cube_id, card_id, mult) VALUES (?, ?, ?)', (cube_id, uuid.UUID(card_id), mult))
        db.commit()
        file.close()


def create_covdb(db=connect('data/site.db')):
    cur = db.cursor()
    cur.execute("""CREATE TABLE Covariance (
                        card1 UUID,
                        card2 UUID,
                        cov REAL,
                        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (card1, card2))""")
    pass


def compute_covariances(_i=-1, _j=-1, db=connect('data/site.db')):
    cur = db.cursor()
    card_ids = list(map(lambda x: x[0],cur.execute('SELECT DISTINCT card_id FROM incidence ').fetchall()))
    num_cubes = cur.execute('SELECT COUNT(DISTINCT cube_id) FROM Incidence').fetchone()[0]
    expected = dict()
    for card in card_ids:
        # print(card)
        expected[card] = cur.execute('SELECT SUM(mult), card_id FROM incidence WHERE card_id=? GROUP BY card_id', (card,)).fetchone()[0] / num_cubes
        # print(expected[card])
    def compute(i,j):
        exp_a = expected[card_ids[i]]
        exp_b = expected[card_ids[j]]
        # print(exp_a)
        try:
            # breakpoint()
            (cov, count) = cur.execute(f"""SELECT SUM( (COALESCE(A.mult, 0) - {exp_a}) * (COALESCE(B.mult, 0) - {exp_b})), COUNT(A.cube_id)
                                FROM (select * from incidence where card_id=?) A
                                FULL OUTER JOIN (select * from incidence where card_id=?) B
                                ON A.cube_id = B.cube_id""", (card_ids[i], card_ids[j])).fetchone()
            count += (exp_a * exp_b) * (num_cubes - count)
            if cov == None or cov== 0:
                return
            cov /= num_cubes
            # print(cov)
            (card_a, card_b) = sorted((card_ids[i], card_ids[j]))
            cur.execute('INSERT OR REPLACE INTO Covariance VALUES (?,?,?)', (card_a, card_b, cov))
        except (RuntimeError, TypeError, NameError) as e:
            print(e)
            print(f'({i}, {j}): {exp_a}, {exp_b}')
    if _i != -1 and _j != -1:
        compute(_i, _j)
    elif _i != -1:
        i = _i
        ind = 0
        n = len(card_ids)
        for j in range(len(card_ids)):
                    compute(i, j)
                    ind = ind + 1
                    if ind % 1000 == 0:
                        print(f'computed {ind/1000}k of {n/1000} cards')
                        db.commit()                        
                        pass
        pass
    else:
        n = len(card_ids)
        n = n*(n-1)/2
        # pairs = list(n * (n - 1)/2)
        ind = 0
        for i in range(len(card_ids)):
                for j in range(i):
                    compute(i, j)
                    ind = ind + 1
                    if ind % 1000 == 0:
                        print(f'computed {ind/1000}k of {n/1000} pairs')
                        db.commit()                        
                        pass
    db.commit()                
                # print(cov)
    pass
# delete_incidence_db()
# create_incidence_db()
#populate_incidence_db()
