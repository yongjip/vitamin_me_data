import sys
import json
import glob
import pandas as pd
import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
sys.path.append('../')
from vitamin_me import iHerbWebPageParser, iHerbWebPageParserBS, WebPage, change_default_country
import time

input_data_loc = 'data/products_html_pages/products_html_pages_*.json'
output_loc = 'data/products.csv'


CHROMEDRIVER_PATH = "./chromedriver"

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('start-maximized') #
options.add_argument('--no-sandbox') # Bypass OS security model
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")

driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)


files = glob.glob(input_data_loc)
files.sort()

output = []
for file in files:
    print(file)
    with open(file, 'r') as f:
        data = json.load(f)
    product_ids = list(data.keys())

    for product_id, html in tqdm.tqdm(data.items()):
        try:
            parser = iHerbWebPageParser(html)
            row = [product_id] + parser.parse_product_page()
            output.append(row)
        except Exception as e:
            print(product_id)
            url = f'https://iherb.com/pr/a/{product_id}'
            driver.get(url)
            time.sleep(3)
            change_default_country(driver, 'US')
            html = driver.execute_script("return document.documentElement.outerHTML")

            html = WebPage(html)
            html.clean_source()
            html.remove_excess_whitespace()
            html = html.get_source()

            parser = iHerbWebPageParser(html)
            row = [product_id] + parser.parse_product_page()
            output.append(row)
            data[product_id] = html


df = pd.DataFrame(output, columns=['product_id'] + parser.column_names)

# df.cate_info = df.cate_info.map(lambda x: str(x))
# df = df.drop_duplicates()
# final_df = df[~df.currency.isna()]

final_df = df[~df.upc.isna()]

final_df.to_csv(output_loc, index=False)

