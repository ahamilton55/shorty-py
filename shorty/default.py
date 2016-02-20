#!/usr/bin/env python3

import sqlite3

from flask import Blueprint, g, redirect, render_template
from flask.ext.api import status


default_handlers = Blueprint('default_handlers', __name__)


def get_orig_url(conn, short_link):
    c = conn.cursor()
    c.execute("SELECT orig_url FROM short_links WHERE short_link = ? LIMIT 1",
                       [short_link])
    db_rtn = c.fetchone()
    if db_rtn:
        return db_rtn[0]
    else:
        return None


@default_handlers.route('/', defaults={'path': ''})
@default_handlers.route('/<path:path>')
def root(path):
    if path == '':
        return render_template("index.html")

    try:
        orig_url = get_orig_url(g.db, path)
    except sqlite3.DatabaseError as e:
        return "", status.HTTP_500_INTERNAL_SERVER_ERROR

    if orig_url:
        return redirect(orig_url, status.HTTP_301_MOVED_PERMANENTLY)
    else:
        return "Link not found", status.HTTP_404_NOT_FOUND
