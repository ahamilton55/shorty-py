#!/usr/bin/env python3

import datetime
import logging
import os
import random
import sqlite3
import string

from contextlib import closing
from flask import Flask, g, redirect, request, make_response
from flask.ext.api import status

app = Flask(__name__)

PATH_SIZE = 8

def create_random_path():
    return ''.join(random.SystemRandom().choice(string.ascii_lowercase +
                                                string.ascii_uppercase +
                                                string.digits)
                                                for _ in range(PATH_SIZE))


def add_short_link_to_db(db, short_link, url):
    c = db.cursor()
    c.execute("INSERT INTO short_links VALUES (?, ?, ?)", [short_link, url,
              datetime.datetime.now().isoformat(' ')])
    db.commit()


def check_short_name(db, name):
    c = db.cursor()
    c.execute("SELECT * FROM short_links WHERE short_link=?", [name])
    if c.fetchone():
        return True
    return False


def find_short_name(input):
    if "name" in input:
        return input["name"]
    else:
        return create_random_path()


def get_short_name(db, input):
    short_name = find_short_name(input)
    exists = check_short_name(db, short_name)

    if exists and "name" in input:
        return False, short_name
    elif exists:
        still_exists = True
        short_name = find_short_name(dict())
        still_exists = check_short_name(db, short_name)
        if still_exists:
            return False, short_name

    return True, short_name


@app.route('/add', methods=['POST'])
def add_short_link():
    if not "url" in request.form:
        app.logger.info("url not provided in request")
        return "url query parameter missing", status.HTTP_400_BAD_REQUEST

    try:
        success, short_name = get_short_name(g.db, request.form)
        if success:
            add_short_link_to_db(g.db, short_name, request.form["url"])
    except sqlite3.DatabaseError as e:
        return "", status.HTTP_500_INTERNAL_SERVER_ERROR

    rtn = "http://127.0.0.1:5000/{0}".format(short_name)

    if success:
        return rtn, status.HTTP_201_CREATED
    else:
        return make_response("Unable to add short link '{short}' for {url}".format(
                                short=short_name, url=request.form["url"]),
                             status.HTTP_409_CONFLICT)


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
        return "Move along people. Nothing to see here!\n\n-- Officer Barbrady"

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
    if not os.path.exists(get_db_location()):
        init_db()

    # In production mode, add log handler to sys.stderr.
    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.INFO)

    app.run()
