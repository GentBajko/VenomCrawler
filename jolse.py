from multiprocessing import Pool
from utils.jobs import jobs
from venom import Venom
import dill


class Jolse(Venom):
    starting_url = 'https://jolse.com/category/skincare/1018'
    column_names = ['Brand', 'Product', 'Price', 'Discounted Price']
    xpaths = ['//tr[@class="prd_brand_css  xans-record-"]//td/span[2]',
              '//div[@class="headingArea "]/h2',
              '//td/span/strong[@id="span_product_price_text"]',
              '//td/span/strong[@id="span_product_price_sales"]']
    product_xpath = '//div[contains(@class, "normalpackage")]//p[@class="name"]/a'
    regex = {'Price': r'\d+\.\d+', 'Discounted Price': r'\d+\.\d+'}
    last_page_xpath = '//li[@class="xans-record-"]/a[@class="this"]'
    last_page_arrow = '//p[@class="last"]'
    page_query = 'page='


if __name__ == '__main__':
    jolse = Jolse("Jolse")
    jolse.calculate_urls().get_services_urls().scrape()
