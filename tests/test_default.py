#!/usr/bin/env python3

import shorty
import sqlite3
import unittest

from mock import Mock, patch

from flask.ext.api import status


class ShortyTestGetOrigURL(unittest.TestCase):
    @patch('shorty.sqlite3')
    def test_get_orig_url_good(self, mock_sqlite3):
        mock_sqlite3.connect().cursor().fetchone.return_value = ['good_test']
        rtn = shorty.default.get_orig_url(mock_sqlite3.connect(), 'test')
        assert rtn == 'good_test'

    @patch('shorty.sqlite3')
    def test_get_orig_url_bad(self, mock_sqlite3):
        mock_sqlite3.connect().cursor().fetchone.return_value = None
        rtn = shorty.default.get_orig_url(mock_sqlite3.connect(), 'badtest')
        assert rtn == None

class ShortyDefaultRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = shorty.app.test_client()

    def test_root(self):
        rtn = self.app.get('/')
        assert 'Move along people. Nothing to see here!' in rtn.data.decode('utf-8')
        assert rtn.status_code == status.HTTP_200_OK

    @patch('shorty.default.get_orig_url', return_value='https://google.com/')
    @patch('shorty.sqlite3.connect')
    def test_good_short_link(self, mock_sqlite3_connect, mock_get_orig_url):
        rtn = self.app.get('/testlink')
        assert rtn.location == 'https://google.com/'
        assert rtn.status_code == status.HTTP_301_MOVED_PERMANENTLY

    @patch('shorty.default.get_orig_url', return_value=None)
    @patch('shorty.sqlite3.connect')
    def test_bad_short_link(self, mock_sqlite3_connect, mock_get_orig_url):
        rtn = self.app.get('/badlink')
        assert 'Link not found' in rtn.data.decode('utf-8')
        assert rtn.status_code == status.HTTP_404_NOT_FOUND

    @patch('shorty.default.get_orig_url', side_effect=sqlite3.DatabaseError)
    @patch('shorty.sqlite3.connect')
    def test_short_link_db_exception(self, mock_sqlite3_connect,
                                     mock_get_orig_url):
        rtn = self.app.get('/somelink')
        assert rtn.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
