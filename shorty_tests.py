#!/usr/bin/env python3

import shorty
import sqlite3
import unittest

from mock import Mock, patch

from flask.ext.api import status


class ShortyCheckShortName(unittest.TestCase):
    @patch('sqlite3.connect')
    def test_check_short_name_good(self, mock_sqlite3):
        mock_sqlite3.cursor().fetchone.return_value = None
        rtn = shorty.check_short_name(mock_sqlite3, "test")
        assert rtn == False

    @patch('sqlite3.connect')
    def test_check_short_name_bad(self, mock_sqlite3):
        mock_sqlite3.cursor().fetchone.return_value = ['blah']
        rtn = shorty.check_short_name(mock_sqlite3, "test")
        assert rtn == True


class ShortyGetShortName(unittest.TestCase):
    @patch('shorty.check_short_name', return_value=True)
    @patch('sqlite3.connect')
    def test_get_short_name_bad_custom(self, mock_sqlite3, mock_check_short_name):
        short_name = "test"
        rtn_success, rtn_short_name = shorty.get_short_name(mock_sqlite3, {"name": short_name})
        assert rtn_success == False
        assert rtn_short_name == short_name

    @patch('shorty.check_short_name', return_value=True)
    @patch('sqlite3.connect')
    def test_get_short_name_bad(self, mock_sqlite3, mock_check_short_name):
        rtn_success, rtn_short_name = shorty.get_short_name(mock_sqlite3,
                                                               {})
        assert rtn_success == False


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


class ShortyTestGetOrigURL(unittest.TestCase):
    @patch('shorty.sqlite3')
    def test_get_orig_url_good(self, mock_sqlite3):
        mock_sqlite3.connect().cursor().fetchone.return_value = ['good_test']
        rtn = shorty.get_orig_url(mock_sqlite3.connect(), 'test')
        assert rtn == 'good_test'

    @patch('shorty.sqlite3')
    def test_get_orig_url_bad(self, mock_sqlite3):
        mock_sqlite3.connect().cursor().fetchone.return_value = None
        rtn = shorty.get_orig_url(mock_sqlite3.connect(), 'badtest')
        assert rtn == None

class ShortyDefaultRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = shorty.app.test_client()

    def test_root(self):
        rtn = self.app.get('/')
        assert 'Move along people. Nothing to see here!' in rtn.data.decode('utf-8')
        assert rtn.status_code == status.HTTP_200_OK

    @patch('shorty.get_orig_url', return_value='https://google.com/')
    @patch('shorty.sqlite3.connect')
    def test_good_short_link(self, mock_sqlite3_connect, mock_get_orig_url):
        rtn = self.app.get('/testlink')
        assert rtn.location == 'https://google.com/'
        assert rtn.status_code == status.HTTP_301_MOVED_PERMANENTLY

    @patch('shorty.get_orig_url', return_value=None)
    @patch('shorty.sqlite3.connect')
    def test_bad_short_link(self, mock_sqlite3_connect, mock_get_orig_url):
        rtn = self.app.get('/badlink')
        assert 'Link not found' in rtn.data.decode('utf-8')
        assert rtn.status_code == status.HTTP_404_NOT_FOUND

    @patch('shorty.get_orig_url', side_effect=sqlite3.DatabaseError)
    @patch('shorty.sqlite3.connect')
    def test_short_link_db_exception(self, mock_sqlite3_connect,
                                     mock_get_orig_url):
        rtn = self.app.get('/somelink')
        assert rtn.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


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

    @patch('shorty.get_short_name', return_value=(True, ""))
    @patch('shorty.add_short_link_to_db')
    @patch('shorty.sqlite3.connect')
    def test_bad_db_add_method(self, mock_sqlite3_connect,
                               mock_add_short_link_to_db, mock_get_short_name):
        mock_add_short_link_to_db.side_effect = sqlite3.DatabaseError
        rtn = self.app.post('/add', data=dict(url="https://google.com/"))
        assert rtn.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @patch('shorty.get_short_name', return_value=(False, "conflict"))
    @patch('shorty.sqlite3')
    def test_add_method_conflict(self, mock_sqlite3_connect,
                               mock_get_short_name):
        rtn = self.app.post('/add', data=dict(url="https://google.com/"))
        assert rtn.status_code == status.HTTP_409_CONFLICT

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


class ShortyTestRandomPath(unittest.TestCase):
    def test_random_path_length(self):
        rtn = shorty.create_random_path()
        assert len(rtn) == shorty.PATH_SIZE

    def test_random_path_random(self):
        rtn1 = shorty.create_random_path()
        rtn2 = shorty.create_random_path()
        assert rtn1 != rtn2

class ShortyTestInitDB(unittest.TestCase):
    @patch('shorty.sqlite3.connect')
    def test_init_db(self, mock_sqlite3_connect):
        shorty.init_db()


if __name__ == "__main__":
    unittest.main()
