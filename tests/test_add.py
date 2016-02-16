#!/usr/bin/env python3

import shorty
import sqlite3
import unittest

from shorty import add
from mock import Mock, patch

from flask.ext.api import status


class ShortyCheckShortName(unittest.TestCase):
    @patch('sqlite3.connect')
    def test_check_short_name_good(self, mock_sqlite3):
        mock_sqlite3.cursor().fetchone.return_value = None
        rtn = shorty.add.check_short_name(mock_sqlite3, "test")
        assert rtn == False

    @patch('sqlite3.connect')
    def test_check_short_name_bad(self, mock_sqlite3):
        mock_sqlite3.cursor().fetchone.return_value = ['blah']
        rtn = shorty.add.check_short_name(mock_sqlite3, "test")
        assert rtn == True


class ShortyGetShortName(unittest.TestCase):
    @patch('shorty.add.check_short_name', return_value=True)
    @patch('sqlite3.connect')
    def test_get_short_name_bad_custom(self, mock_sqlite3, mock_check_short_name):
        short_name = "test"
        rtn_success, rtn_short_name = shorty.add.get_short_name(mock_sqlite3, {"name": short_name})
        assert rtn_success == False
        assert rtn_short_name == short_name

    @patch('shorty.add.check_short_name', return_value=True)
    @patch('sqlite3.connect')
    def test_get_short_name_bad(self, mock_sqlite3, mock_check_short_name):
        rtn_success, rtn_short_name = shorty.add.get_short_name(mock_sqlite3, {})
        assert rtn_success == False


class ShortyAddRouteTestCases(unittest.TestCase):
    def setUp(self):
        self.app = shorty.app.test_client()

    @patch('shorty.sqlite3')
    def test_add(self, mock_sqlite3):
        mock_sqlite3.connect().cursor().fetchone.return_value = False
        rtn = self.app.post('/add', data=dict(url="https://google.com/"))
        assert rtn.status_code == status.HTTP_201_CREATED

    @patch('shorty.sqlite3')
    def test_add_custom(self, mock_sqlite3):
        mock_sqlite3.connect().cursor().fetchone.return_value = False
        rtn = self.app.post('/add', data=dict(url="https://google.com/",
                                              name="custom_name"))
        assert rtn.status_code == status.HTTP_201_CREATED

    @patch('shorty.sqlite3')
    def test_missing_param(self, mock_sqlite3):
        rtn = self.app.post('/add', data={})
        assert rtn.status_code == status.HTTP_400_BAD_REQUEST

    @patch('shorty.sqlite3')
    def test_bad_add_method(self, mock_sqlite3):
        rtn = self.app.put('/add', data=dict(url="https://google.com/"))
        assert rtn.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @patch('shorty.add.get_short_name', return_value=(True, ""))
    @patch('shorty.add.add_short_link_to_db')
    @patch('shorty.sqlite3.connect')
    def test_bad_db_add_method(self, mock_sqlite3_connect,
                               mock_add_short_link_to_db, mock_get_short_name):
        mock_add_short_link_to_db.side_effect = sqlite3.DatabaseError
        rtn = self.app.post('/add', data=dict(url="https://google.com/"))
        assert rtn.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @patch('shorty.add.get_short_name', return_value=(False, "conflict"))
    @patch('shorty.sqlite3')
    def test_add_method_conflict(self, mock_sqlite3_connect,
                               mock_get_short_name):
        rtn = self.app.post('/add', data=dict(url="https://google.com/"))
        assert rtn.status_code == status.HTTP_409_CONFLICT


class ShortyTestRandomPath(unittest.TestCase):
    def test_random_path_length(self):
        rtn = shorty.add.create_random_path()
        assert len(rtn) == shorty.add.PATH_SIZE

    def test_random_path_random(self):
        rtn1 = shorty.add.create_random_path()
        rtn2 = shorty.add.create_random_path()
        assert rtn1 != rtn2
