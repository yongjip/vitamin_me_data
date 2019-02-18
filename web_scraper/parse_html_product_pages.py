import sys
import json
import glob
import pandas as pd
import tqdm
sys.path.append('../')
from vitamin_me import iHerbWebPageParser, iHerbWebPageParserBS


input_data_loc = 'data/products_html_pages/products_html_pages_*.json'
excel_output_loc = 'data/products.xlsx'


files = glob.glob(input_data_loc)
files.sort()

output = []
for file in files:
    print(file)
    with open(file, 'r') as f:
        data = json.load(f)
    product_ids = list(data.keys())

    for product_id, html in tqdm.tqdm(data.items()):
        parser = iHerbWebPageParser(html)
        row = [product_id] + parser.parse_product_page()
        output.append(row)


df = pd.DataFrame(output, columns=['product_id'] + parser.column_names)
df.to_excel(excel_output_loc, index=False)
