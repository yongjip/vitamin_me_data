import sys
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import dask.dataframe as dd
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from time import sleep
from lxml.html.clean import Cleaner
from collections import defaultdict
import tqdm
import os
import json
import requests


def get_logger(name):
    import logging.handlers
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '[%(levelname)-8s] %(asctime)s [%(filename)s] [%(funcName)s:%(lineno)d] %(message)s',
        '%Y-%m-%d %H:%M:%S')
    sh.setFormatter(formatter)

    logger.addHandler(sh)
    return logger


class WebScraper:

    def __init__(self):
        from selenium.webdriver.chrome.options import Options
        self.url = None
        self.chrome_driver = None
        self.chrome_options = Options()

    def requests_get(self, url):
        page = requests.get(url)
        return str(page.content) # byte to str

    def chrome_driver_get(self, url, sleep_sec=3):
        self.chrome_driver.get(url)
        sleep(sleep_sec)
        page = self.chrome_driver.execute_script("return document.documentElement.outerHTML")
        return page

    def initialize_chrome_driver(self, driver_path):
        from selenium import webdriver
        self.chrome_driver = webdriver.Chrome(driver_path, options=self.chrome_options)


class WebPage:

    def __init__(self, source=None):
      self.source = source

    def __repr__(self):
        return self.source

    def clean_source(self, rm_javascript=True, rm_style=True):
        cleaner = Cleaner()
        cleaner.javascript = rm_javascript  # This is True because we want to activate the javascript filter
        cleaner.style = rm_style  # This is True because we want to activate the styles & stylesheet filter
        cleaned_page = cleaner.clean_html(self.source)
        self.source = cleaned_page

    def remove_excess_whitespace(self):
        self.source = re.sub(r'\s+', r' ', self.source)

    def get_source(self):
        return self.source


class iHerbWebPageParserWithBS:
    def __init__(self, source):
        self.source = source
        self.soup = BeautifulSoup(self.soup)

    def find_price(self):
        pricing_soup = self.soup.find('section', {'id': 'pricing'})
        discontinued_soup = self.soup.find('div', {'class': 'discontinued-container'})
        if pricing_soup:
            master_price = pricing_soup.find('section', {'id': 'product-msrp'}).s.text
            price = pricing_soup.find(id='price').text.strip()
        elif discontinued_soup:
            master_price = 'Discontinued'
            price = 'Discontinued'
        else:
            master_price = None
            price = None
        return master_price, price

    def find_categories(self):
        category_regex = r'<a (?:class="last" |)href="https://(?:\w{0,3}\.)iherb.com/(?:c/|)([\w\-\_]+)">'

        category_raw = str(self.soup.find('div', {'id': 'breadCrumbs'}))
        category_split = category_raw.split('<br/>')
        cate_list = []
        for cate_i in category_split[:-1]:
            cates = re.findall(category_regex, cate_i, re.IGNORECASE)
            cate_list.append(cates)
        return cates

    def find_upc(self):
        # re.findall(upc_regex, self.source, re.IGNORECASE)
        # spec_soup = self.soup.find('ul', {'id': 'product-specs-list'})
        upc_eng_regex = r'<li>UPC Code: <span>(\d+)<\/span>'
        upc = re.search(upc_eng_regex, self.source, re.IGNORECASE).group(1)
        return upc


class iHerbWebPageParserWithRegex:
    def __init__(self, source):
        self.source = source

    def find_price(self):
        pricing_soup = self.soup.find('section', {'id': 'pricing'})
        discontinued_soup = self.soup.find('div', {'class': 'discontinued-container'})
        if pricing_soup:
            master_price = pricing_soup.find('section', {'id': 'product-msrp'}).s.text
            price = pricing_soup.find(id='price').text.strip()
        elif discontinued_soup:
            master_price = 'Discontinued'
            price = 'Discontinued'
        else:
            master_price = None
            price = None
        return master_price, price

    def find_categories(self):
        cate_section_regex = r'(?=<div id="breadCrumbs">)(.*?)(?=<\/div>)'
        category_regex = r'<a (?:class="last" |)href="https://(?:\w{0,3}\.)iherb.com/(?:c/|)([\w\-\_]+)">'
        category_raw = re.findall(cate_section_regex, self.source, re.IGNORECASE)[0]

        category_split = category_raw.split('<br/>')

        cate_list = []
        for cate_i in category_split[:-1]:
            cates = re.findall(category_regex, cate_i, re.IGNORECASE)
            cate_list.append(cates)
        return cates

    def find_upc(self):
        upc_eng_regex = r'<li>UPC Code: <span>(\d+)<\/span>'
        upc = re.search(upc_eng_regex, self.source, re.IGNORECASE).group(1)
        return upc


if __name__ == '__main__':
    CHROMEDRIVER_PATH = "./chromedriver"

    scraper = WebScraper()
    scraper.chrome_options.add_argument('--disable-gpu')
    # scraper.chrome_options.add_argument('--headless')
    scraper.chrome_options.add_argument('start-maximized')
    scraper.chrome_options.add_argument('--no-sandbox') # Bypass OS security model
    scraper.chrome_options.add_argument('disable-infobars')
    scraper.chrome_options.add_argument("--disable-extensions")
    scraper.initialize_chrome_driver(CHROMEDRIVER_PATH)

    url = f'https://iherb.com/pr/a/51659'
    page_req = str(scraper.requests_get(url))

    page_sel = scraper.chrome_driver_get(url)

    page_req = WebPage(page_req)
    page_req.clean_source()
    page_req.remove_excess_whitespace()
    page_req = page_req.get_source()

    page_sel = WebPage(page_sel)
    page_sel.clean_source()
    page_sel.remove_excess_whitespace()
    page_sel = page_sel.get_source()

    soup_req = BeautifulSoup(page_req)
    soup_sel = BeautifulSoup(page_sel)

