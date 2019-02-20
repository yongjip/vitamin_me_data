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


class iHerbWebPageParser:

    def __init__(self, source):
        self.source = source
        self.preprocessed_source = re.sub(r'\s+', ' ', self.source)
        self.msrp_regex = r'class="col\-xs\-15 col\-md\-16 price">\s*<s>(.*?)</s>'
        self.price_regex = r'id="price">\s*(.*?)</div>'
        self.split_currency_regex = r'([^\d])([\d|\.]+)'
        self.discontinued_regex = r'<p class="discontinued-title">'
        self.cate_section_regex = r'(?=<div id="breadCrumbs">)(.*?)(?=<\/div>)'
        self.category_regex = r'<a (?:class="last" |)href="https://(?:\w{0,3}\.)iherb.com/(?:c/|)([\w\-\_]+)">'
        self.product_name_regex = r'<h1 id="name">(.*?)</h1>'
        self.url_regex = r'https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*)'
        self.brand_name_regex = r'<div id="brand">\s*\w+\s*<a href="{}"> <span>\s*(.*?)\s*</span>'.format(self.url_regex)
        self.upc_eng_regex = r'<li>UPC Code: <span>\s*(\d+)\s*<\/span>'
        self.page_404_regex = r'\<div id\=\"error\-page\-404\"\>'

        self.column_names = ['cate_info', 'upc', 'product_name', 'brand_name', 'currency', 'master_price', 'price']

    def find_product_name(self):
        return re.search(self.product_name_regex, self.source).group(1)

    def find_brand_name(self):
        return re.search(self.brand_name_regex, self.source).group(1)

    def find_price_info(self):
        discontinued_tag = re.search(self.discontinued_regex, self.source, re.IGNORECASE | re.DOTALL)
        master_price_tag = re.search(self.msrp_regex, self.source, re.IGNORECASE | re.DOTALL)
        price_tag = re.search(self.price_regex, self.source, re.IGNORECASE | re.DOTALL)
        master_price_tag = master_price_tag if master_price_tag else price_tag
        if price_tag:
            master_price_with_currency = master_price_tag.group(1).strip()
            price_with_currency = price_tag.group(1).strip()
            currency = re.search(self.split_currency_regex, price_with_currency, re.IGNORECASE | re.DOTALL).group(1)
            master_price = re.search(self.split_currency_regex, master_price_with_currency, re.IGNORECASE | re.DOTALL).group(2)
            price = re.search(self.split_currency_regex, price_with_currency, re.IGNORECASE | re.DOTALL).group(2)
            return currency, float(master_price), float(price)
        elif discontinued_tag:
            currency = 'Discontinued'
            master_price = None
            price = None
        else:
            currency = None
            master_price = None
            price = None
        return currency, master_price, price

    def find_categories(self):
        category_raw = re.search(self.cate_section_regex, self.source, re.IGNORECASE | re.DOTALL)
        if category_raw is None:
            return None
        category_raw = category_raw.group()
        category_split = category_raw.split('<br>')

        cate_list = []
        for cate_i in category_split[:-1]:
            cates = re.findall(self.category_regex, cate_i, re.IGNORECASE | re.DOTALL)
            cate_list.append(cates)
        return cate_list

    def find_upc(self):
        upc = re.search(self.upc_eng_regex, self.source, re.IGNORECASE | re.DOTALL).group(1)
        return upc

    def parse_product_page(self):
        page_404 = re.search(self.page_404_regex, self.source)
        if page_404:
            # print('page doesn\'t exists')
            return [None] * 7
        cate_info = self.find_categories()
        upc = self.find_upc()
        product_name = self.find_product_name()
        brand_name = self.find_brand_name()
        price_info = self.find_price_info()
        currency = price_info[0]
        master_price = price_info[1]
        price = price_info[2]
        return [cate_info, upc, product_name, brand_name, currency, master_price, price]


class iHerbWebPageParserBS(iHerbWebPageParser):

    def __init__(self, source):
        iHerbWebPageParser.__init__(self, source)
        self.soup = BeautifulSoup(self.source, 'html.parser')

    def find_product_name(self):
        product_name = self.soup.find('h1', {'id': 'name'}).text
        return product_name.strip()

    def find_brand_name(self):
        brand_name = self.soup.find('div', {'id': 'brand'}).span.text
        return brand_name.strip()

    def find_price_info(self):
        pricing_soup = self.soup.find('section', {'id': 'pricing'})
        discontinued_soup = self.soup.find('div', {'class': 'discontinued-container'})
        if pricing_soup:
            master_price_with_currency = pricing_soup.find('section', {'id': 'product-msrp'}).s.text.strip()
            price_with_currency = pricing_soup.find(id='price').text.strip()

            currency = re.search(self.split_currency_regex, master_price_with_currency, re.IGNORECASE | re.DOTALL).group(1)
            master_price = re.search(self.split_currency_regex, master_price_with_currency, re.IGNORECASE | re.DOTALL).group(2)
            price = re.search(self.split_currency_regex, price_with_currency, re.IGNORECASE | re.DOTALL).group(2)
            return currency, float(master_price), float(price)
        elif discontinued_soup:
            currency = 'Discontinued'
            master_price = None
            price = None
        else:
            currency = None
            master_price = None
            price = None
        return currency, master_price, price

    def find_categories(self):
        category_raw = str(self.soup.find('div', {'id': 'breadCrumbs'}))
        category_split = category_raw.split('<br/>')
        cate_list = []
        for cate_i in category_split[:-1]:
            cates = re.findall(self.category_regex, cate_i, re.IGNORECASE | re.DOTALL)
            cate_list.append(cates)
        return cate_list


class iHerbNavigator:

    def __init__(self, driver):
        self.driver = driver

    def change_default_country(self, new_default_country='KR'):
        country_select = self.driver.find_element_by_class_name('country-select')
        old_default_country = country_select.text
        if new_default_country == old_default_country:
            return f'current default country is already {new_default_country}'
        country_select.click()

        search_input = self.driver.find_element_by_class_name('search-input')
        search_input.click()

        country_code_flags = self.driver.find_elements_by_class_name('country-code-flag')

        for elem in country_code_flags:
            # print(elem.text)
            if elem.text == new_default_country:
                elem.click()
                break

        sleep(3)
        submit_default_lan_change = self.driver.find_element_by_css_selector("input[type='submit']")
        submit_default_lan_change.click()
        sleep(5)
        return print(f'changed default language from {old_default_country} to {new_default_country}')


# change default language
def change_default_country(driver, new_default_country='KR'):
    country_select = driver.find_element_by_class_name('country-select')
    old_default_country = country_select.text
    if new_default_country == old_default_country:
        return f'current default country is already {new_default_country}'
    country_select.click()

    search_input = driver.find_element_by_class_name('search-input')
    search_input.click()

    country_code_flags = driver.find_elements_by_class_name('country-code-flag')

    for elem in country_code_flags:
        # print(elem.text)
        if elem.text == new_default_country:
            elem.click()
            break

    sleep(3)
    submit_default_lan_change = driver.find_element_by_css_selector("input[type='submit']")
    submit_default_lan_change.click()
    sleep(5)
    return print(f'changed default language from {old_default_country} to {new_default_country}')


if __name__ == '__main__':

    from random import shuffle

    product_ids = list(range(0, 90001))
    shuffle(product_ids)

    CHROMEDRIVER_PATH = "./chromedriver"

    scraper = WebScraper()
    scraper.chrome_options.add_argument('--disable-gpu')
    scraper.chrome_options.add_argument('--headless')
    scraper.chrome_options.add_argument('start-maximized')
    scraper.chrome_options.add_argument('--no-sandbox') # Bypass OS security model
    scraper.chrome_options.add_argument('disable-infobars')
    scraper.chrome_options.add_argument('--disable-extensions')
    scraper.initialize_chrome_driver(CHROMEDRIVER_PATH)

    for product_id in product_ids:
        url = f'https://iherb.com/pr/a/{product_id}'

        page_sel = scraper.chrome_driver_get(url)
        change_default_country(scraper.chrome_driver, 'US')
        page_sel = scraper.chrome_driver_get(url)

        page_sel = WebPage(page_sel)
        page_sel.clean_source()
        page_sel.remove_excess_whitespace()
        page_sel = page_sel.get_source()

        # soup_req = BeautifulSoup(page_req)
        soup_sel = BeautifulSoup(page_sel)
        source = str(soup_sel.contents[0])

        parser = iHerbWebPageParser(source)
        parsed = parser.parse_product_page()
        print(product_id, parsed)

    soup = BeautifulSoup(source)
    parserbs = iHerbWebPageParserBS(source)
    print(parserbs.parse_product_page())

    # page_req = str(scraper.requests_get(url))
    # page_req = WebPage(page_req)
    # page_req.clean_source()
    # page_req.remove_excess_whitespace()
    # page_req = page_req.get_source()

    # parserbs = iHerbWebPageParserBS(source)
    # print(parserbs.parse_product_page())

    # discontinued = re.search(discontinued_regex, source, re.IGNORECASE | re.DOTALL).group(1)
    # master_price = re.search(msrp_regex, source, re.IGNORECASE | re.DOTALL).group(1)
    # price = re.search(price_regex, source, re.IGNORECASE | re.DOTALL).group(1)
    #
    # re.search(currency_regex, price, re.IGNORECASE | re.DOTALL).group(1)
