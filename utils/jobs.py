from pathos.multiprocessing import Pool

from Venom import VenomCrawler


def initiateVenom(*args):
    venom = VenomCrawler(*args)
    if venom.next_xpath:
        venom.pagination().get_services_urls().scrape()
    elif venom.search_xpath:
        venom.search().get_services_urls().scrape()
    elif venom.page_query:
        venom.calculate_urls().get_services_urls().scrape()
    elif venom.product_xpath:
        venom.get_services_urls().scrape()
    else:
        venom.scrape()


def Venom(name: str, starting_url: str, column_names: list, xpaths: list, next_xpath: str = None,
          product_xpath: str = None, url_queries: dict = None, page_query: str = None, page_steps: int = None,
          last_page_xpath: str = None, last_page_arrow: str = None, search_xpath: str = None,
          search_terms: str = None, load_more: str = None, regex: dict = None, predefined_url_list: list = None,
          error_xpaths: list = None, chunksize: int = None):
    if not chunksize:
        chunksize = 1
    map_lists = [(name, starting_url, column_names, xpaths, next_xpath, product_xpath, url_queries, page_query,
                  page_steps, last_page_xpath, last_page_arrow, search_xpath, search_terms, load_more, regex,
                  predefined_url_list, error_xpaths, chunksize, i) for i in range(chunksize)]
    pool = Pool(chunksize)
    pool.starmap(initiateVenom, map_lists)


if __name__ == '__main__':
    pass
