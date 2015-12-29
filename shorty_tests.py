#!/usr/bin/env python3

import shorty
import unittest

from flask.ext.api import status

class ShortyDefaultRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = shorty.app.test_client()

    def test_root(self):
        rtn = self.app.get('/')
        assert 'Hello world' in rtn.data.decode('utf-8')
        assert rtn.status_code == status.HTTP_200_OK

    def test_good_short_link(self):
        rtn = self.app.get('/test_link')
        assert rtn.location == 'https://google.com'
        assert rtn.status_code == status.HTTP_301_MOVED_PERMANENTLY

    def test_bad_short_link(self):
        rtn = self.app.get('/bad_link')
        assert 'Link not found' in rtn.data.decode('utf-8')
        assert rtn.status_code == status.HTTP_404_NOT_FOUND


class ShortyAddRouteTestCases(unittest.TestCase):
    def setUp(self):
        self.app = shorty.app.test_client()

    def test_add(self):
        rtn = self.app.put('/add', data=dict(url="https://google.com/"))
        assert rtn.status_code == status.HTTP_201_CREATED

    def test_missing_param(self):
        rtn = self.app.put('/add', data={})
        assert rtn.status_code == status.HTTP_400_BAD_REQUEST

    def test_bad_add_method(self):
        rtn = self.app.post('/add', data=dict(url="https://google.com/"))
        assert rtn.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


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
if __name__ == "__main__":
    unittest.main()
