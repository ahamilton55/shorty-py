#!/usr/bin/env python3

import shorty
import sqlite3
import unittest

from mock import Mock, patch

from flask.ext.api import status


class ShortyDeleteRouteTestCases(unittest.TestCase):
    def setUp(self):
        self.app = shorty.app.test_client()

    def test_good_delete(self):
        rtn = self.app.delete('/delete', data=dict(short_id="testid01"))
        assert rtn.status_code == status.HTTP_200_OK

    def test_bad_delete(self):
        rtn = self.app.delete('/delete', data=dict(short_id="badtest"))
        assert rtn.status_code == status.HTTP_404_NOT_FOUND

    def test_bad_delete_method(self):
        rtn = self.app.post('/delete', data=dict(short_id="testid01"))
        assert rtn.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
