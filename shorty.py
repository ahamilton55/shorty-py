#!/usr/bin/env python3

import datetime
import logging
import os
import random
import sqlite3
import string

from contextlib import closing
from flask import Flask, g, redirect, request
from flask.ext.api import status

app = Flask(__name__)

PATH_SIZE = 8

def create_random_path():
    return ''.join(random.SystemRandom().choice(string.ascii_lowercase +
                                                string.ascii_uppercase +
                                                string.digits)
                                                for _ in range(PATH_SIZE))


def add_new_short_link(conn, short_link, url):
    c = conn.cursor()
    c.execute("INSERT INTO short_links VALUES (?, ?, ?)", [short_link, url,
              datetime.datetime.now().isoformat(' ')])
    conn.commit()


@app.route('/add', methods=['PUT'])
def add_short_link():
    if not "url" in request.form:
        app.logger.info("url not provided in request")
        return "url query parameter missing", status.HTTP_400_BAD_REQUEST

    random_path = create_random_path()
    try:
        add_new_short_link(g.db, random_path, request.form["url"])
    except sqlite3.DatabaseError as e:
        return "", status.HTTP_500_INTERNAL_SERVER_ERROR

    rtn = "http://127.0.0.1:5000/{0}".format(random_path)

    return rtn, status.HTTP_201_CREATED


@app.route('/delete', methods=['DELETE'])
def delete_short_link():
    if request.form['short_id'] == "testid01":
        return "Successfully deleted short link", status.HTTP_200_OK
    else:
        return "Short link not found", status.HTTP_404_NOT_FOUND


def get_orig_url(conn, short_link):
    c = conn.cursor()
    c.execute("SELECT orig_url FROM short_links WHERE short_link = ? LIMIT 1",
                       [short_link])
    db_rtn = c.fetchone()
    if db_rtn:
        return db_rtn[0]
    else:
        return None


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def root(path):
    if path == '':
        return "Hello world"

    try:
        orig_url = get_orig_url(g.db, path)
    except sqlite3.DatabaseError as e:
        return "", status.HTTP_500_INTERNAL_SERVER_ERROR

    if orig_url:
        return redirect(orig_url, status.HTTP_301_MOVED_PERMANENTLY)
    else:
        return "Link not found", status.HTTP_404_NOT_FOUND


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def get_db_location():
    if "DB_LOCATION" in app.config:
        return app.config["DB_LOCATION"]
    else:
        return os.getenv('SHORTY_DB', './shorty.db')

def connect_db():
    db_location = get_db_location()
    return sqlite3.connect(db_location)


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


if __name__ == "__main__":
    # In production mode, add log handler to sys.stderr.

    if not os.path.exists(get_db_location()):
        init_db()

    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.INFO)

    app.run()
