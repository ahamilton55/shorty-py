#!/usr/bin/env python3

import logging

from flask import Flask, redirect, request
from flask.ext.api import status

app = Flask(__name__)


@app.route('/add', methods=['PUT'])
def add_short_link():
    if not "url" in request.form:
        app.logger.info("url not provided in request")
        return "url query parameter missing", status.HTTP_400_BAD_REQUEST

    return "Short link added", status.HTTP_201_CREATED


@app.route('/delete', methods=['DELETE'])
def delete_short_link():
    if request.form['short_id'] == "testid01":
        return "Successfully deleted short link", status.HTTP_200_OK
    else:
        return "Short link not found", status.HTTP_404_NOT_FOUND

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def root(path):
    app.logger.info(path)
    if path == '':
        return "Hello world"

    if path == 'test_link':
        return redirect('https://google.com', status.HTTP_301_MOVED_PERMANENTLY)
    else:
        return "Link not found", status.HTTP_404_NOT_FOUND


if __name__ == "__main__":
    # In production mode, add log handler to sys.stderr.
    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.INFO)

    app.run()
