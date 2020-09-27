from venom import Venom
from utils.jobs import filesplitter

cols = ['Brand', 'Product', 'Price', 'Discounted Price']
xpath = ['//tr[@class="prd_brand_css  xans-record-"]//td/span[2]',
         '//div[@class="headingArea "]/h2',
         '//td/span/strong[@id="span_product_price_text"]',
         '//td/span/strong[@id="span_product_price_sales"]']
start_url = 'https://jolse.com/category/skincare/1018'
last_page = '//p[@class="last"]'
page = 'page='
steps = 1
last_page_xpath = '//li[@class="xans-record-"]/a[@class="this"]'
regular_exp = {'Price': r'\d+\.\d+', 'Discounted Price': r'\d+\.\d+'}
prod = '//div[contains(@class, "normalpackage")]//p[@class="name"]/a'


if __name__ == '__main__':
    jolse = Venom(starting_url=start_url, column_names=cols, xpaths=xpath, regex=regular_exp, product_xpath=prod)

    jolse.calculate_urls(page_query=page, page_steps=steps, last_page_xpath=last_page_xpath,
                         last_page_arrow=last_page).get_services_urls().scrape()
