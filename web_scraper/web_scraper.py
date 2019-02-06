import sys
from bs4 import BeautifulSoup
import requests
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep


url = 'https://kr.iherb.com/r/a/71684'


CHROMEDRIVER_PATH = "./chromedriver"

options = Options()
# options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('start-maximized') #
options.add_argument('--no-sandbox') # Bypass OS security model
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")

driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)

driver.get(url)

sleep(4)
html = driver.execute_script("return document.documentElement.outerHTML")

soup = BeautifulSoup(html, 'html.parser')


reviews = soup.findAll("div", {"class": "review-core-section"})
print(len(reviews))

start_pat = r'<svg class="icon icon-stars_(\d)0 stars-rating">'
for review_soup in reviews:
    stars = review_soup.find('svg',  {'class': 'icon'})
    m = re.search(start_pat, str(stars))
    stars = m.group(1) if m else None
    print(stars)
    headline = review_soup.find('h3', {'class': 'review-headline'}).text
    posted_date = review_soup.find('span', {'class': 'posted-date'}).text
    posted_date = review_soup.find('span', {'class': 'posted-date'}).text
    review_body = review_soup.find('div', {'class': 'review-text'}).text


print(headline, posted_date, stars, review_body, sep='\n')

review_soup.find('use')


paging = soup.find("div", {"class": "paging"})
current_page_num = paging.find('button', {'class': 'selected-page'}).text

driver.find_elements_by_class_name('button')

page = driver.find_elements_by_class_name('page')
driver.find_elements_by_class_name('selected-page')
next_page = driver.find_elements_by_class_name('arrow-button')[1]


page.click()


# headers = {'Content-Type': 'application/json; charset=utf-8',
#             'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'}

# headers = {'Content-Type': 'application/json; charset=utf-8',
#             'User-Agent' : 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_1 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Mobile/15C153'}

# r = requests.get(url, headers=headers)
# content = r.content

# with open('test.html', 'wb') as f:
#     f.write(content)