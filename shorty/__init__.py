#!/usr/bin/env python3

import logging
import os
import sqlite3

from contextlib import closing
from flask import Flask, g

from shorty.add import add_handlers
from shorty.default import default_handlers
from shorty.delete import delete_handlers

app = Flask(__name__)


@app.before_request
def before_request():
    g.db = connect_db()
    g.logger = app.logger


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def get_db_location():
    if "DB_LOCATION" in app.config:
        return app.config["DB_LOCATION"]
    else:
        return os.getenv('SHORTY_DB', '/tmp/shorty.db')


def connect_db():
    db_location = get_db_location()
    return sqlite3.connect(db_location)


def init_db():
    if not os.path.exists(get_db_location()) or get_db_location == ':memory:':
        with closing(connect_db()) as db:
            with app.open_resource('resources/schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()


init_db()

# In production mode, add log handler to sys.stderr.
app.logger.addHandler(logging.StreamHandler())
app.logger.setLevel(logging.INFO)

# setup blueprints
app.register_blueprint(add_handlers)
app.register_blueprint(default_handlers)
app.register_blueprint(delete_handlers)
