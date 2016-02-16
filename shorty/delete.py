#!/usr/bin/env python3

from flask import Blueprint, request
from flask.ext.api import status


delete_handlers = Blueprint('delete_handlers', __name__)


@delete_handlers.route('/delete', methods=['DELETE'])
def delete_short_link():
    if request.form['short_id'] == "testid01":
        return "Successfully deleted short link", status.HTTP_200_OK
    else:
        return "Short link not found", status.HTTP_404_NOT_FOUND
