import glob
import pandas as pd
import json

import tqdm

input_data_loc = '../data/reviews_in_json/review_pages_*.json'
output_loc = '../data/reviews.csv'


CHROMEDRIVER_PATH = "./chromedriver"

files = glob.glob(input_data_loc)
files.sort()

output = []

col_names = ['productId', 'postedDate', 'languageCode', 'ratingValue', 'reviewTitle', 'reviewText', 'helpfulYes', 'helpfulNo', 'score']

for file in tqdm.tqdm(files):
    # print(file)
    with open(file, 'r') as f:
        data = json.load(f)
    product_ids = list(data.keys())

    for product_id, reviews in data.items():
        reviews = reviews[product_id]
        for idx, review in reviews.items():
            score = review['score']
            reviewTitle = review['reviewTitle']
            reviewText = review['reviewText']
            ratingValue = review['ratingValue']
            helpfulYes = review['helpfulYes']
            helpfulNo = review['helpfulNo']
            productId = review['productId']
            postedDate = review['postedDate']
            languageCode = review['languageCode']
            row = [productId, postedDate, languageCode, ratingValue, reviewTitle, reviewText, helpfulYes, helpfulNo, score]
            output.append(row)

df = pd.DataFrame(output, columns=col_names)

df.to_csv(output_loc, index=False)
