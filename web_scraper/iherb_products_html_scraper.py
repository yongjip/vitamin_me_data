import os
import re
import json
import tqdm
from datetime import datetime
from time import sleep
from lxml.html.clean import Cleaner
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

size = 10000

start_product_id = 10001
end_product_id = 90000

output_dir = 'data/products_html_pages/'
output_json_name = 'products_html_pages_{start_id}_{end_id}.json'
CHROMEDRIVER_PATH = "./chromedriver"

os.makedirs(output_dir, exist_ok=True)

cleaner = Cleaner()
cleaner.javascript = True # This is True because we want to activate the javascript filter
cleaner.style = True # This is True because we want to activate the styles & stylesheet filter


options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('start-maximized') #
options.add_argument('--no-sandbox') # Bypass OS security model
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")

driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)


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


logger = get_logger('html_scraper')

product_raw_html_dict = {}

for product_id in tqdm.tqdm(range(start_product_id, end_product_id+1)):
    url = f'https://iherb.com/pr/a/{product_id}'
    driver.get(url)
    html = driver.execute_script("return document.documentElement.outerHTML")
    cleaned_html = cleaner.clean_html(html)
    minified_html = re.sub(r'\s+', r' ', cleaned_html)
    product_raw_html_dict[product_id] = minified_html

    if product_id % size == 0 or end_product_id == product_id:
        if product_id % size == 0:
            product_id_starting_from = product_id - size + 1
        else:
            num_processed = product_id % size - 1
            product_id_starting_from = product_id - num_processed
        output_destination = output_dir + output_json_name.format(start_id=product_id_starting_from, end_id=product_id)
        current_time = datetime.now()
        # print(f'[{current_time}]Dumping: {output_destination}', sep='\n')
        sleep(0.2)
        logger.info(f'Dumping: {output_destination}')
        with open(output_destination, 'w') as f:
            json.dump(product_raw_html_dict, f)
        product_raw_html_dict = {}
