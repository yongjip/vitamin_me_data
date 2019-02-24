import json
import sys
import os
import tqdm
import pandas as pd
from collections import defaultdict
from datetime import datetime
sys.path.append('../')
from vitamin_me import iHerbReviewGatherer, get_logger


size = 10000
limit = 1000

output_dir = 'data/reviews_in_json/'
os.makedirs(output_dir, exist_ok=True)
output_json_name = 'review_pages_{start_id}_{end_id}.json'

input_data_loc = 'data/products.csv'
df = pd.read_csv(input_data_loc)

products_having_reviews = df.loc[df.review_exists.isin([True]), 'product_id'].tolist()

logger = get_logger('review_getherer')
product_review_dict = defaultdict(lambda: {})

getherer = iHerbReviewGatherer()
getherer.limit = limit

for pid in tqdm.tqdm(products_having_reviews):
    getherer.pull_raw_reviews(pid)
    reviews = getherer.clean_reviews()

    product_review_dict[pid] = reviews

    if pid % size == 0 or pid == products_having_reviews[-1]:
        if pid % size == 0:
            product_id_starting_from = pid - size + 1
        else:
            num_processed = pid % size - 1
            product_id_starting_from = pid - num_processed
        output_destination = output_dir + output_json_name.format(start_id=product_id_starting_from, end_id=pid)
        current_time = datetime.now()
        # print(f'[{current_time}]Dumping: {output_destination}', sep='\n')
        logger.info(f'Dumping: {output_destination}')
        with open(output_destination, 'w') as f:
            json.dump(product_review_dict, f)
        product_review_dict = {}
