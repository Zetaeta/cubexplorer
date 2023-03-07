
import json
import math
import os
import sqlite3
import uuid
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

def create_corr_db(db=connect('data/site.db')):
    cur = db.cursor()
    cur.execute("""CREATE TABLE Correlation (
                        card1 UUID,
                        card2 UUID,
                        corr REAL,
                        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (card1, card2))""")
    pass

def get_bottom(n, card_id, db=connect('data/site.db')):
    cur = db.cursor()
    return cur.execute(f'SELECT card2, corr FROM correlation WHERE card1=? UNION SELECT card1, corr FROM correlation WHERE card2=? ORDER BY corr LIMIT {n}', (card_id, card_id)).fetchall()

def get_top(n, card_id, db=connect('data/site.db')):
    cur = db.cursor()
    return cur.execute(f'SELECT card2, corr FROM correlation WHERE card1=? AND card2 <> ? UNION SELECT card1, corr FROM correlation WHERE card2=? AND card1 <> ? ORDER BY corr DESC LIMIT {n}', (card_id, card_id, card_id, card_id)).fetchall()
    
def compute_cov(a,b,cur, expected, num_cubes, corr=True):
        exp_a = expected[a]
        exp_b = expected[b]
        # print(exp_a)
        # breakpoint()
        (cov, count) = cur.execute(f"""SELECT SUM( (COALESCE(A.mult, 0) - {exp_a}) * (COALESCE(B.mult, 0) - {exp_b})), COUNT(COALESCE(A.cube_id, B.cube_id))
                            FROM (select * from incidence where card_id=?) A
                            FULL OUTER JOIN (select * from incidence where card_id=?) B
                            ON A.cube_id = B.cube_id""", (a, b)).fetchone()
        if a==uuid.UUID("34841228-31ac-48ac-b6d6-486b5e1e07dd"):
            print(f'cov={cov:9.4f}, a={a},b={b},count={count}')
        cov += (exp_a * exp_b) * (num_cubes - count)
        if cov == None or cov== 0:
            return
        cov /= num_cubes
        # print(cov)
        (card_a, card_b) = sorted((a, b))
        cur.execute('INSERT OR REPLACE INTO Covariance (card1, card2, cov) VALUES (?,?,?)', (card_a, card_b, cov))
        if a==uuid.UUID("34841228-31ac-48ac-b6d6-486b5e1e07dd"):
            print(f'cov={cov:9.4f}, a={a},b={b},count={count}')
            pass
        if corr:
            var_a = cur.execute('SELECT cov FROM covariance WHERE card1=? AND card2=?', (a, a)).fetchone()[0]
            var_b = cur.execute('SELECT cov FROM covariance WHERE card1=? AND card2=?', (b, b)).fetchone()[0]
            correl=cov / math.sqrt(var_a * var_b)
            cur.execute('INSERT OR REPLACE INTO Correlation (card1, card2, corr) VALUES (?,?,?)', (card_a, card_b, correl))
            if abs(correl)>1:
                print(f'cov={cov:9.4f}, var_a={var_a:9.4f}, var_b={var_b:9.4f}, corr={correl:9.4f} a={a},b={b}')


def compute_variances(db=connect('data/site.db'), card_ids=None, num_cubes=None):
    cur = db.cursor()
    if not card_ids:
        card_ids = list(map(lambda x: x[0],cur.execute('SELECT DISTINCT card_id FROM incidence ').fetchall()))
    if not num_cubes:
        num_cubes = cur.execute('SELECT COUNT(DISTINCT cube_id) FROM Incidence').fetchone()[0]
    expected = dict()
    for card in card_ids:
        # print(card)
        expected[card] = cur.execute('SELECT SUM(mult), card_id FROM incidence WHERE card_id=? GROUP BY card_id', (card,)).fetchone()[0] / num_cubes
    for card in card_ids:
        compute_cov(card, card, cur, expected, num_cubes, corr=False)
    db.commit()


def compute_covariances(_i=-1, _j=-1, db=connect('data/site.db')):
    cur = db.cursor()
    card_ids = list(map(lambda x: x[0],cur.execute('SELECT DISTINCT card_id FROM incidence ').fetchall()))
    num_cubes = cur.execute('SELECT COUNT(DISTINCT cube_id) FROM Incidence').fetchone()[0]
    expected = dict()
    for card in card_ids:
        # print(card)
        expected[card] = cur.execute('SELECT SUM(mult), card_id FROM incidence WHERE card_id=? GROUP BY card_id', (card,)).fetchone()[0] / num_cubes
        # print(expected[card])
    
    if _i != -1 and _j != -1:
        a = _i
        b = _j
        if isinstance(a,int):
            a = card_ids[a]
        if isinstance(b,int):
            b = card_ids[b]
        compute_cov(a, b,cur, expected, num_cubes)
    elif _i != -1:
        i = _i        
        if isinstance(i,int):
            i = card_ids[i]
        ind = 0
        n = len(card_ids)
        for j in range(len(card_ids)):
                    compute_cov(i, card_ids[j],cur, expected, num_cubes)
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
                    try:
                        compute_cov(i, j,cur, expected, num_cubes)
                        ind = ind + 1
                        if ind % 1000 == 0:
                            print(f'computed {ind/1000}k of {n/1000} pairs')
                            db.commit()
                    except (RuntimeError, TypeError, NameError) as e:
                        print(e)
                        # print(f'({a}, {b}): {exp_a}, {exp_b}')
    db.commit()                
                # print(cov)
    pass
# delete_incidence_db()
# create_incidence_db()
#populate_incidence_db()
