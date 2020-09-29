import os
from multiprocessing import Pool
from venom import Venom
import asyncio

splits = 10

lists = [str(i) for i in range(splits)]

processes = [f'jolse.py {splits} {i}' for i in lists]


def run_process(process):
    os.system(f'python {process}')


def jobs(**kwargs):
    chunksize = kwargs.get('chunksize')

    class Crawler(Venom):
        starting_url = kwargs.get('starting_url')
        column_names = kwargs.get('column_names')
        xpaths = kwargs.get('xpaths')
        error_xpaths = kwargs.get('error_xpaths')
        url_queries = kwargs.get('url_queries')
        product_xpath = kwargs.get('product_xpath')
        regex = kwargs.get('regex')
        next_xpath = kwargs.get('next_xpath')
        chunksize = kwargs.get('chunksize')
        page_query = kwargs.get('page_query')
        page_steps = kwargs.get('page_steps')
        last_page_xpath = kwargs.get('last_page_xpath')
        last_page_arrow = kwargs.get('last_page_arrow')
        search_xpath = kwargs.get('search_xpath')
        search_terms = kwargs.get('search_terms')
        predefined_url_list = kwargs.get('predefined_url_list')
        load_more = kwargs.get('predefined_url_list')
        save_file = True

    return chunksize, [(chunksize, i) for i in range(chunksize)], Crawler


if __name__ == '__main__':
    pool = Pool(processes=splits)
    pool.map(run_process, processes)
    # chunksize, chunks, Crawler = jobs(starting_url='https://jolse.com/category/skincare/1018',
    #      column_names=['Brand', 'Product', 'Price', 'Discounted Price'],
    #      xpaths=['//tr[@class="prd_brand_css  xans-record-"]//td/span[2]',
    #              '//div[@class="headingArea "]/h2',
    #              '//td/span/strong[@id="span_product_price_text"]',
    #              '//td/span/strong[@id="span_product_price_sales"]'],
    #      product_xpath='//div[contains(@class, "normalpackage")]//p[@class="name"]/a',
    #      regex={'Price': r'\d+\.\d+', 'Discounted Price': r'\d+\.\d+'},
    #      last_page_xpath='//li[@class="xans-record-"]/a[@class="this"]',
    #      last_page_arrow='//p[@class="last"]', page_query='?page=', page_steps=1, chunksize=2)
    # pool = Pool(chunksize)
    # pool.map(Crawler, chunks)
