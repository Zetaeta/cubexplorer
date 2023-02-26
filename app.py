from flask import Flask, send_from_directory, g, request, jsonify
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
from api.ApiHandler import ApiHandler
import sqlite3
import json

DATABASE = 'data/site.db'
    
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

app = Flask(__name__, static_url_path="", static_folder="frontend/build")
CORS(app)
api = Api(app)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/", defaults={"path": ""})
def serve(path):
    return send_from_directory(app.static_folder, "index.html")

@app.route("/tree", methods=["POST"])
def get_tree():
    print(request.json)
    path = request.json["path"]
    tree = get_tree()
    cur_node = tree
    cards = get_cards(list(map(lambda x: x["card"], path)))
    for (card, path_entry) in zip(cards, path):
        condition = cur_node["condition"]
        print(card)
        print(condition)
        assert card["name"] == condition["card"]
        if path_entry["comp"] == ">":
            cur_node = cur_node["right"]
        else:
            cur_node = cur_node["left"]
    if isinstance(cur_node, str):
        return jsonify({
            "type": "leaf",
            "cube": cur_node[0:-4],
            "path": path
        })
    else:
        condition = cur_node["condition"]
        card_id = get_card_by_name(condition["card"])
        print(card_id)
        return jsonify({
            "type": "node",
            "path": path,
            "condition": {
                "card": card_id,
                "cut": condition["cut"]
            }
        })


def get_card_id(card_name):
    cur = get_db().cursor()
    return cur.execute(f'SELECT oracle_id FROM Cards WHERE name = "{card_name}"').fetchone()[0]


def get_card_by_name(card_name):
    db = get_db()
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    return dict(cur.execute(f'SELECT * FROM Cards WHERE name = "{card_name}"').fetchone())


def get_cards(card_ids):
    db = get_db()
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    return [dict(cur.execute(f'SELECT * FROM Cards WHERE oracle_id = "{card_id}"').fetchone()) for card_id in card_ids]


def get_tree():
    file = open('data/tree.json',"r")
    tree = json.load(file)
    file.close()
    return tree


api.add_resource(ApiHandler, "/flask/hello")
