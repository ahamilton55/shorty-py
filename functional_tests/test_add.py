#1/usr/bin/env python3

import unittest

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException

class TestAddShortLink(unittest.TestCase):
    def setUp(self):
        #self.driver = webdriver.PhantomJS()
        self.display = Display(visible=0, size=(1440, 900))
        self.display.start()
        self.driver = webdriver.Firefox()

    def tearDown(self):
        self.driver.close()
        self.driver.quit()
        self.display.stop()

    def test_add_good(self):
        self.driver.get('http://192.168.99.1:5000/')
        self.driver.find_element_by_id('url').send_keys('https://google.com/')
        self.driver.find_element_by_id('add_button').click()

        assert "New link successfully created." in self.driver.page_source

    def test_add_good_custom(self):
        self.driver.get('http://192.168.99.1:5000/')
        self.driver.find_element_by_id('url').send_keys('https://google.com/')
        self.driver.find_element_by_id('name').send_keys('test_name')
        self.driver.find_element_by_id('add_button').click()

        assert "New link successfully created." in self.driver.page_source

    def test_add_zbad_conflict(self):
        self.driver.get('http://192.168.99.1:5000/')
        self.driver.find_element_by_id('url').send_keys('https://google.com/')
        self.driver.find_element_by_id('name').send_keys('test_name')
        self.driver.find_element_by_id('add_button').click()

        try:
            WebDriverWait(self.driver,
                          2).until(expected_conditions.alert_is_present(),
                                  "Time out while waiting on alert")
            alert = self.driver.switch_to_alert()
            assert alert.text == "Name test_name already exists"
            alert.accept()
        except TimeoutException:
            assert False


#    def test_add_another(self):
#        self.driver.find_element_by_id('create_another').click()
#
#        assert self.driver.find_element_by_id('default').
