#!/usr/bin/env bash


python iherb_products_html_scraper.py # ETA: days
python parse_html_product_pages.py # ETA: minutes
python gather_iherb_reviews.py #ETA: hours
python create_reviews_table.py