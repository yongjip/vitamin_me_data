import json
import glob
from bs4 import BeautifulSoup
import re
import tqdm
import pandas as pd

input_data_loc = 'data/products_html_pages/products_html_pages_*.json'
output_loc = 'data/true_if_review_exists.csv'

files = glob.glob(input_data_loc)
files.sort()


def review_exists(product_id):
    html = data[product_id]
    soup = BeautifulSoup(html, 'html.parser')

    page_404 = soup.find('div', {'id': "error-page-404"})
    if page_404:
        # print('page doesn\'t exists')
        return None

    none_if_review_exists = soup.find('a', {'class': 'write-review'})
    if none_if_review_exists is None:
        return True

    return False


def review_exists_regex(product_id):
    html = data[product_id]
    page_404 = re.search(r'\<i class\=\"error\-404\-icon icon\-sadness\"\>\<\/i\>', html, re.IGNORECASE)
    if page_404:
        # print('page doesn\'t exists')
        return None
    none_if_review_exists = re.search(r'\<a class\=\"write\-review\" href\=', html, re.IGNORECASE)
    if none_if_review_exists is None:
        return True
    return False


review_cnt = []
for file in files:
    print(file)
    with open(file, 'r') as file:
        data = json.load(file)
    product_ids = list(data.keys())

    for product_id in tqdm.tqdm(product_ids):
        true_if_review = review_exists_regex(product_id)
        review_cnt.append([product_id, true_if_review])


df = pd.DataFrame(review_cnt, columns=['product_id', 'review_exists'])
df.to_csv(output_loc, index=False)