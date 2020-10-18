from pathos.multiprocessing import Pool

from Venom.Venom import Paginate
from threading import Thread


def initiateVenom(*args):
    Paginate(*args).run_threads()


def Venom(name: str, starting_url: str, column_names: list, xpaths: list, next_xpath: str = None,
          product_xpath: str = None, url_queries: dict = None, page_query: str = None, page_steps: int = None,
          last_page_xpath: str = None, last_page_arrow: str = None, search_xpath: str = None,
          search_terms: str = None, load_more: str = None, regex: dict = None, predefined_url_list: list = None,
          error_xpaths: list = None, chunksize: int = None):
    if not chunksize:
        chunksize = 1
    map_lists = [(name, starting_url, column_names, xpaths,
                  next_xpath, product_xpath, chunksize, i) for i in range(chunksize)]
    pool = Pool(chunksize)
    pool.starmap(initiateVenom, map_lists)


if __name__ == '__main__':
    pass
