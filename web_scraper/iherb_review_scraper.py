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
from selenium.webdriver.common.keys import Keys

# review url
default_country = 'KR' # US
base_url = 'https://kr.iherb.com/'


REVIEW_STAR_PATTERN = r'<svg class="icon icon-stars_(\d)0 stars-rating">'

REVIEW_YES_NO_CNT_PATTERN_KR = r'(네|아니요) \((\d+)\)'
REVIEW_YES_NO_CNT_PATTERN_US = r'(Yes|No) \((\d+)\)'

REVIEW_DATE_PATTERN_KR = '게시 날짜: %m월 %d %Y'
REVIEW_DATE_PATTERN_US = 'Posted on %B %d %Y'


if default_country == 'KR':
    REVIEW_YES_NO_CNT_PATTERN = REVIEW_YES_NO_CNT_PATTERN_KR
    REVIEW_DATE_PATTERN = REVIEW_DATE_PATTERN_KR
    review_language = "Korean"
elif default_country == 'US':
    REVIEW_YES_NO_CNT_PATTERN = REVIEW_YES_NO_CNT_PATTERN_US
    REVIEW_DATE_PATTERN = REVIEW_DATE_PATTERN_US
    review_language = 'English' # 'All'

review_column_names = ['rundt', 'product_id', 'customer_id', 'headline', 'stars','posted_date', 'review_body', 'helpful_cnt', 'not_helpful_cnt']


# url = 'https://kr.iherb.com/r/a/42963'

CHROMEDRIVER_PATH = "./chromedriver"

options = Options()
# options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('start-maximized') #
options.add_argument('--no-sandbox') # Bypass OS security model
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")


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


def scrape_review(soup):
    assert isinstance(soup, bs4.element.Tag)
    rundt = datetime.now().date()

    customer_id = soup.find_all('a', href=True)[0]['href'].split('/')[-1]
    product_id = soup.find_all('a', href=True)[1]['href'].split('/')[-1] # 0 = customer url, 1 == product url

    stars = soup.find('svg', {'class': 'icon'})
    m = re.search(REVIEW_STAR_PATTERN, str(stars))
    stars = m.group(1)

    headline = soup.find('h3', {'class': 'review-headline'}).text
    posted_date = soup.find('span', {'class': 'posted-date'}).text
    posted_date_dt = datetime.strptime(posted_date, REVIEW_DATE_PATTERN)
    review_body = soup.find('div', {'class': 'review-text'}).text

    helpfulness = soup.find_all('button', {'class': 'btn btn-default btn-xs'})
    helpful = helpfulness[0].text
    helpful_cnt = re.search(REVIEW_YES_NO_CNT_PATTERN, str(helpful)).group(2)
    not_helpful = helpfulness[1].text
    not_helpful_cnt = re.search(REVIEW_YES_NO_CNT_PATTERN, str(not_helpful)).group(2)

    return [rundt, int(product_id), customer_id, headline, int(stars), posted_date_dt, review_body, int(helpful_cnt), int(not_helpful_cnt)]


driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)
driver.get(base_url)
sleep(4)
change_default_country(default_country)

# product_id = 23452
product_id = 71684

url = f'https://kr.iherb.com/r/a/{product_id}'

driver.get(url)
sleep(4)
page_remaining = 1

review_data = []
while page_remaining > 0:
    try:
        print('remaining at least:', page_remaining)
        change_default_country(default_country)

        html = driver.execute_script("return document.documentElement.outerHTML")
        sleep(3)

        soup = BeautifulSoup(html, 'html.parser')

        reviews = soup.findAll("div", {"class": 'review-row'})
        review_cnt = len(reviews)

        # while review_cnt > 0
        review_data_i = []
        for review_soup in reviews:
            row_i = scrape_review(review_soup)
            review_data_i.append(row_i)

        df = pd.DataFrame(review_data_i, columns=review_column_names)
        print(df)

        paging = soup.find("div", {"class": "paging"})
        current_page_num = int(paging.find('button', {'class': 'selected-page'}).text)

        page_num_elements = paging.find_all('button', {'class': 'page'})
        page_numbers = [int(elem.text) for elem in page_num_elements]

        page_remaining = [1 if current_page_num < page_i else 0 for page_i in page_numbers]
        page_remaining = sum(page_remaining)
        if page_remaining > 0:
            # go to the next page
            next_page_elem = driver.find_elements_by_class_name('arrow-button')[1]
            # coordinates = next_page_elem.location_once_scrolled_into_view  # returns dict of X, Y coordinates
            # driver.execute_script('window.scrollTo({}, {});'.format(coordinates['x'], coordinates['y']))
            # driver.execute_script("return arguments[0].scrollIntoView(true);", next_page_elem)
            driver.execute_script("arguments[0].scrollIntoView();", next_page_elem)
            driver.execute_script("$(arguments[0]).click();", next_page_elem)
            sleep(2)
            next_page_elem.click()
            sleep(1)
            driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
            sleep(4)
            review_data += review_data_i
        else:
            review_data += review_data_i
    except Exception as e:
        print(e)
        driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
        sleep(3)
        pass


df = pd.DataFrame(review_data, columns=review_column_names)
# df.to_csv('test.csv', index=False)
# 'Show Original Language'
# dd = f"//input[contains(.,'Show Original Language')]"
# driver.find_elements_by_css_selector("input[type='hidden']")
