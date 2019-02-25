import sys
from bs4 import BeautifulSoup
import requests
import time
import re
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

# review url

CATEGORY_REGEX = r'<a (?:class="last" |)href="https://(?:\w{0,3}\.)iherb.com/(?:c/|)(.+)">'
CATEGORY_REGEX = r'<a (?:class="last" |)href="https://(?:\w{0,3}\.)iherb.com/(?:c/|)([\w-_]+)">'

product_id = 86987
product_id = 45987 # Discontinued
product_id = 46987 # no page

soup = BeautifulSoup(html, 'html.parser')

page_404 = soup.find('div', {'id': "error-page-404"})
if page_404:
    print('page doesn\'t not exists')


'stock-status'
"""
# If no review:
[<a class="write-review" href="https://www.iherb.com/ugc/product/86987/review">Write a Review</a>,
 <a class="write-review" href="https://www.iherb.com/ugc/product/86987/review">Write a Review</a>]
"""

empty_if_review_exists = soup.find_all('a', {'class': 'write-review'})
no_review = len(empty_if_review_exists)
print(no_review)

# if no_review == 0, skip scraping reviews

"""
<div id="breadCrumbs">
<a href="https://www.iherb.com/BrandsAZ">Brands A-Z</a>
<a class="last" href="https://www.iherb.com/c/Natural-Factors">Natural Factors</a>
<br/>
<a href="https://www.iherb.com/c/Categories">Categories</a>
<a href="https://www.iherb.com/c/Herbs-Homeopathy">Herbs &amp; Homeopathy</a>
<a href="https://www.iherb.com/c/Herbs">Herbs</a>
<a class="last" href="https://www.iherb.com/c/Berberine-Barberry">Berberine (Barberry)</a>
<br/>
</div>
"""

'Categories">Categories</a> <a href="https://www.iherb.com/c/Supplements">Supplements</a> <a href="https://www.iherb.com/c/Antioxidants">Antioxidants</a> <a class="last" href="https://www.iherb.com/c/Coenzyme-Q10-CoQ10'
CATEGORY_REGEX = r'<a (?:class="last" |)href="https://(?:\w{0,3}\.)iherb.com/(?:c/|)(.+)">'

category_raw = str(soup_sel.find('div', {'id': 'breadCrumbs'}))
category_split = category_raw.split('<br/>')


for cate_i in category_split[:-1]:
    cates = re.findall(CATEGORY_REGEX, cate_i, re.IGNORECASE)
    print(cates)

"""
<section id="pricing">
<section id="product-msrp">
<div class="row">
<div class="col-xs-9 col-md-8 label">
                                                    MSRP:
                                                </div>
<div class="col-xs-15 col-md-16 price">
<s>$27.95</s>
</div>
</div>
</section>
<section id="product-price">
<div class="row">
<div class="col-xs-9 col-md-8 label">
                                            Our Price:
                                        </div>
<div class="col-xs-15 col-md-16 price our-price" id="price">
                                            $19.57
                                        </div>
</div>
<div class="row">
<div class="col-xs-offset-9 col-md-offset-8 col-xs-15 col-md-16 small price-per-unit">
                                                $0.33/Count
                                            </div>
</div>
</section>
<section id="product-discount">
<div class="row">
<div class="col-xs-9 col-md-8 label">
                                                You Save:
                                            </div>
<div class="col-xs-15 col-md-16 discount">
<bdi>$8.38 (<span class="discount-text">30</span>)</bdi>
</div>
</div>
</section>
</section>

"""

pricing_soup = soup.find('section', {'id': 'pricing'})
discontinued_soup = soup.find('div', {'class': 'discontinued-container'})
if pricing_soup:
    master_price = pricing_soup.find('section', {'id': 'product-msrp'}).s.text
    price = pricing_soup.find(id='price').text.strip()
elif discontinued_soup:
    master_price = 'Discontinued'
    price = 'Discontinued'
else:
    master_price = None
    price = None

