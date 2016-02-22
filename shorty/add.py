#!/usr/bin/env python3

import datetime
import random
import sqlite3
import string
import urllib

from flask import Blueprint, escape, g, json, request, make_response
from flask.ext.api import status

PATH_SIZE = 8


add_handlers = Blueprint('add_handlers', __name__)

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


def check_short_name_format(name):
    encoded_name = urllib.parse.urlencode({"name": name})
    if '%' in encoded_name:
        return False

    return True

def check_short_name_exists(db, name):
    c = db.cursor()
    c.execute("SELECT * FROM short_links WHERE short_link=?", [name])
    if c.fetchone():
        return True
    return False


def find_short_name(input):
    if "name" in input and input["name"] != "":
        return input["name"]
    else:
        return create_random_path()


def get_short_name(db, input):
    short_name = find_short_name(input)
    format_ok = check_short_name_format(short_name)

    if not format_ok:
        return False, (status.HTTP_400_BAD_REQUEST,
                       "Name {0} contains unacceptable characters".format(escape(short_name)))

    exists = check_short_name_exists(db, short_name)

    if exists and "name" in input:
        return False, (status.HTTP_409_CONFLICT,
                       "Name {0} already exists".format(short_name))
    elif exists:
        still_exists = True
        short_name = find_short_name(dict())
        still_exists = check_short_name_exists(db, short_name)
        if still_exists:
            return False, (status.HTTP_409_CONFLICT,
                           "Name {0} already exists".format(short_name))

    return True, short_name


@add_handlers.route('/add', methods=['POST'])
def add_short_link():
    if not "url" in request.form:
        g.logger.info("url not provided in request")
        return "url query parameter missing", status.HTTP_400_BAD_REQUEST

    try:
        success, short_name = get_short_name(g.db, request.form)
        if success:
            add_short_link_to_db(g.db, short_name, request.form["url"])
        else:
            error_status = short_name[0]
            error_msg = short_name[1]
    except sqlite3.DatabaseError as e:
        return "", status.HTTP_500_INTERNAL_SERVER_ERROR

    if success:
        parsed_url = urllib.parse.urlparse(request.url_root)

        rtn = "{scheme}://{netloc}/{path}".format(scheme=parsed_url.scheme,
                                                  netloc=parsed_url.netloc,
                                                  path=short_name)

        return make_response(json.jsonify(url=rtn), status.HTTP_201_CREATED)
    else:
        return make_response(json.jsonify(msg=error_msg,
                                          status_code=error_status),
                             error_status)

