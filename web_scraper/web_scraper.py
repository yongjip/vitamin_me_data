import sys
from bs4 import BeautifulSoup
import requests
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


url = 'https://kr.iherb.com/r/a/71684'
# headers = {'Content-Type': 'application/json; charset=utf-8',
#             'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'}

# headers = {'Content-Type': 'application/json; charset=utf-8',
#             'User-Agent' : 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_1 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Mobile/15C153'}

# r = requests.get(url, headers=headers)
# content = r.content

# with open('test.html', 'wb') as f:
#     f.write(content)

CHROMEDRIVER_PATH = "./chromedriver"

options = Options()
# options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('start-maximized') #
options.add_argument('--no-sandbox') # Bypass OS security model
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")

driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)

driver.get("https://kr.iherb.com/r/a/62121")

class_names = ['review-headline', 'posted-date', 'flavor', 'review-text']


class_names = 'review-text line-clamp'
elems = driver.find_elements_by_class_name(class_names)

for elem_set in elems:
    print(elem_set.text)
    print()

elements = []
for class_names in class_names:
    elements.append(driver.find_elements_by_class_name(class_names))


for elem_set in elements[3]:
    print(elem_set.text)
    print()


content = driver.page_source

