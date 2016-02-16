#!/usr/bin/env python3

import shorty
import sqlite3
import unittest

from mock import Mock, patch

from flask.ext.api import status


class ShortyTestConnectDB(unittest.TestCase):
    def setUp(self):
        self.app = shorty.app.test_client()

    @patch('shorty.sqlite3.connect')
    def test_env_value(self, mock_sqlite3_connect):
        shorty.app.config.pop('DB_LOCATION', None)
        rtn = self.app.get('/')
        assert rtn.status_code == status.HTTP_200_OK

    @patch('shorty.sqlite3.connect')
    def test_config_value(self, mock_sqlite3_connect):
        shorty.app.config['DB_LOCATION'] = ':memory:'
        rtn = self.app.get('/')
        assert rtn.status_code == status.HTTP_200_OK
        del shorty.app.config['DB_LOCATION']


class ShortyTestInitDB(unittest.TestCase):
    @patch('shorty.sqlite3.connect')
    def test_init_db(self, mock_sqlite3_connect):
        shorty.init_db()
