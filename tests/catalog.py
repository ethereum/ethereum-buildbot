# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

class Integration(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://ethereum-dapp-catalog.meteor.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
        self.driver.set_window_position(0, 0)
        self.driver.set_window_size(1280, 1200)

    def test_catalog(self):
        driver = self.driver

        try:
            driver.get(self.base_url)
            time.sleep(5)

            driver.save_screenshot('catalog-init.png')

        except Exception as e:
            driver.save_screenshot('catalog-fail.png')
            self.fail(e)

        self.assertEqual([], self.verificationErrors)

        driver.save_screenshot('catalog-passed.png')

        driver.quit()
