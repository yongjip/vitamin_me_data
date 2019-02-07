import sys
from bs4 import BeautifulSoup
import requests
import time
import re
import sys
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import bs4
import pandas as pd
import dask.dataframe as dd
from datetime import datetime

# review url
default_country = 'KR' # US
base_url = 'https://kr.iherb.com/'


CHROMEDRIVER_PATH = "./chromedriver"

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('start-maximized') #
options.add_argument('--no-sandbox') # Bypass OS security model
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")

driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)

# need productid, review count
# product page
product_id = 77144
product_id = 77144
url = f'https://iherb.com/pr/a/{product_id}'
driver.get(url)

html = driver.execute_script("return document.documentElement.outerHTML")

soup = BeautifulSoup(html, 'html.parser')

empty_if_review_exists = soup.find_all('a', {'class': 'write-review'})
no_review = len(empty_if_review_exists)
print(no_review)

soup.find_all('a', {'class': 'last'}) # 0 == brand, 1 == last cate