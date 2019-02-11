from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import pickle
import tqdm


output_pickle_name ='product_raw_html_dict.pickle'

CHROMEDRIVER_PATH = "./chromedriver"

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('start-maximized') #
options.add_argument('--no-sandbox') # Bypass OS security model
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")

driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)

# need productid, review count
# product page
product_raw_html_dict = {}
start_product_id = 0
end_product_id = 90000

print(datetime.now())

for product_id in tqdm.tqdm(range(start_product_id, end_product_id)):
    url = f'https://iherb.com/pr/a/{product_id}'
    driver.get(url)
    html = driver.execute_script("return document.documentElement.outerHTML")
    product_raw_html_dict[product_id] = html

pickle_out = open(output_pickle_name, "wb")
pickle.dump(product_raw_html_dict, pickle_out)
pickle_out.close()


# pickle_in = open(output_pickle_name, "rb")
# example_dict = pickle.load(pickle_in)