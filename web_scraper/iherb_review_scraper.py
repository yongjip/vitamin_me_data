import sys
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import bs4
import pandas as pd


# review url
product_id = 71684
url = f'https://kr.iherb.com/r/a/{product_id}'


default_country = 'KR'
review_language_options = ['All', 'Korean', 'English']
review_language = review_language_options[1]


# url = 'https://kr.iherb.com/r/a/42963'

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


def change_review_language():
    pat = f"//option[contains(.,'{review_language}')]"
    lan_option = driver.find_element_by_xpath(pat)
    lan_option.click()


def click_machine_translation_option():
    # check or uncheck translation option
    translation_option = driver.find_element_by_class_name('translate-reviews-check')
    translation_checkbox = translation_option.find_element_by_css_selector("input[type='checkbox']")
    translation_checkbox.click()


# change default language
def change_default_country(new_default_country='KR'):
    country_select = driver.find_element_by_class_name('country-select')
    sleep(3)
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


change_default_country(default_country)

html = driver.execute_script("return document.documentElement.outerHTML")
soup = BeautifulSoup(html, 'html.parser')

reviews = soup.findAll("div", {"class": 'review-row'})
review_cnt = len(reviews)

#condition: reveiw count > 0 & next page


REVIEW_STAR_PATTERN = r'<svg class="icon icon-stars_(\d)0 stars-rating">'
REVIEW_YES_NO_CNT_PATTERN = r'(Yes|No) \((\d+)\)'
review_column_names = ['product_id', 'customer_id', 'headline', 'stars','posted_date', 'review_body', 'helpful_cnt', 'not_helpful_cnt']


def scrape_review(soup):
    assert isinstance(soup, bs4.element.Tag)
    customer_id = review_soup.find_all('a', href=True)[0]['href'].split('/')[-1]
    product_id = review_soup.find_all('a', href=True)[1]['href'].split('/')[-1] # 0 = customer url, 1 == product url

    stars = soup.find('svg', {'class': 'icon'})
    m = re.search(REVIEW_STAR_PATTERN, str(stars))
    stars = m.group(1)

    headline = soup.find('h3', {'class': 'review-headline'}).text
    posted_date = soup.find('span', {'class': 'posted-date'}).text
    review_body = soup.find('div', {'class': 'review-text'}).text

    helpfulness = soup.find_all('button', {'class': 'btn btn-default btn-xs'})
    helpful = helpfulness[0].text
    helpful_cnt = re.search(REVIEW_YES_NO_CNT_PATTERN, str(helpful)).group(2)
    not_helpful = helpfulness[1].text
    not_helpful_cnt = re.search(REVIEW_YES_NO_CNT_PATTERN, str(not_helpful)).group(2)
    return [int(product_id), customer_id, headline, int(stars), posted_date, review_body, int(helpful_cnt), int(not_helpful_cnt)]


review_data = []
for review_soup in reviews:
    row_i = scrape_review(review_soup)
    review_data.append(row_i)

df = pd.DataFrame(review_data, columns=review_column_names)


paging = soup.find("div", {"class": "paging"})
current_page_num = int(paging.find('button', {'class': 'selected-page'}).text)

page_num_elements = paging.find_all('button', {'class': 'page'})
page_numbers = [int(elem.text) for elem in page_num_elements]

page_remaining = [1 if current_page_num < page_i else 0 for page_i in page_numbers]

if sum(page_remaining) > 0:
    pass

# go to the next page
next_page = driver.find_elements_by_class_name('arrow-button')[1]
next_page.click()



'Show Original Language'
dd = f"//input[contains(.,'Show Original Language')]"
driver.find_elements_by_css_selector("input[type='hidden']")

