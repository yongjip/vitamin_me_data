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

cleaner = Cleaner()
cleaner.javascript = True # This is True because we want to activate the javascript filter
cleaner.style = True # This is True because we want to activate the styles & stylesheet filter

# review url
default_country = 'KR' # US
base_url = 'https://kr.iherb.com/'


if default_country == 'KR':
    review_language = "Korean"
elif default_country == 'US':
    review_language = 'English' # 'All'


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


driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)
driver.get(base_url)
sleep(4)
change_default_country(default_country)


# product_id = 23452

product_review_dict = defaultdict(lambda: '')

product_id = 71684

url = f'https://kr.iherb.com/r/a/{product_id}'

driver.get(url)
sleep(4)
page_remaining = True
current_page_num = 1

while page_remaining is True:
    try:
        print('Page remaining:', page_remaining)

        change_default_country(default_country)
        html_i = driver.execute_script("return document.documentElement.outerHTML")
        sleep(2)

        soup = BeautifulSoup(html_i, 'html.parser')
        paging = soup.find("div", {"class": "paging"})
        current_page_num = int(paging.find('button', {'class': 'selected-page'}).text)

        print('Current page:', current_page_num)

        html_i = cleaner.clean_html(html_i)
        html_i = re.sub(r'\s+', r' ', html_i)
        review_soup = BeautifulSoup(html_i, 'html.parser')
        reviews_html_list = review_soup.findAll("div", {"class": 'review-row'})
        reviews_html_list = [str(elem) for elem in reviews_html_list]
        reviews_html = ' '.join(reviews_html_list)

        page_num_elements = paging.find_all('button', {'class': 'page'})
        page_numbers = [int(elem.text) for elem in page_num_elements]

        page_remaining = True if current_page_num < max(page_numbers) else False
        if page_remaining is True:
            # go to the next page
            next_page_elem = driver.find_elements_by_class_name('arrow-button')[1]
            # coordinates = next_page_elem.location_once_scrolled_into_view  # returns dict of X, Y coordinates
            # driver.execute_script('window.scrollTo({}, {});'.format(coordinates['x'], coordinates['y']))
            # driver.execute_script("return arguments[0].scrollIntoView(true);", next_page_elem)
            driver.execute_script("arguments[0].scrollIntoView();", next_page_elem)
            driver.execute_script("$(arguments[0]).click();", next_page_elem)
            sleep(2)
            driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
            sleep(4)
        product_review_dict[product_id] += reviews_html

    except Exception as e:
        print(e)
        driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
        sleep(3)
        pass

ss = BeautifulSoup(product_review_dict[product_id], 'html.parser').findAll("div", {"class": 'review-row'})
len(ss)
ss = [e.text for e in ss]