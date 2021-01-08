from itertools import product

from selenium.common.exceptions import NoSuchElementException, \
    UnexpectedAlertPresentException
from threading import Thread
from .Composer import Composer
import re


class Venom(Composer):

    def __init__(self, name: str,
                 starting_url: str,
                 column_names: list,
                 xpaths: list,
                 next_xpath: str = None,
                 product_xpath: str = None,
                 url_queries: dict = None,
                 page_query: str = None,
                 page_steps: int = None,
                 last_page_xpath: str = None,
                 last_page_arrow: str = None,
                 search_xpath: str = None,
                 search_terms: str = None,
                 load_more: str = None,
                 regex: dict = None,
                 predefined_url_list: list = None,
                 error_xpaths: list = None,
                 chunksize: int = None,
                 chunk: int = None):
        super(Venom, self).__init__(name, starting_url,
                                    column_names, xpaths,
                                    next_xpath, product_xpath,
                                    url_queries, page_query,
                                    page_steps, last_page_xpath,
                                    last_page_arrow, search_xpath,
                                    search_terms, load_more, regex,
                                    predefined_url_list, error_xpaths,
                                    chunksize, chunk)

    def pagination(self):
        self.urls = iter(self.urls)
        for url in self.urls:
            self.driver.get(url)
            if not self.error():
                while True:
                    self.source.append(self.driver.current_url)
                    if self.product_xpath:
                        self.get_services(self.driver.current_url)
                    try:
                        self.driver.find_element_by_xpath(self.next_xpath).click()
                    except (NoSuchElementException,
                            UnexpectedAlertPresentException):
                        break
        self.save(self.source, 'pages')
        self.save(self.products, 'products')
        return self

    def calculate_urls(self):
        urls = self.urls
        for url in urls:
            self.driver.get(url)
            if not self.error():
                self.wait_to_load(20)
                if self.last_page_arrow:
                    self.wait_to_load(self.last_page_arrow)
                    self.driver.find_element_by_xpath(self.last_page_arrow).click()
                last_page = self.driver.find_element_by_xpath(self.last_page_xpath).text
                last_page = re.search(r'\d+$', last_page).group()
                if self.page_steps == 1:
                    page_range = [str(i) for i in
                                  range(1, (int(last_page) * self.page_steps) + 1, self.page_steps)]
                else:
                    page_range = [str(i) for i in
                                  range(0, int(last_page) * self.page_steps, self.page_steps)]
                tuples = product([url], [self.page_query], page_range)
                new_urls = [''.join(link) for link in tuples]
                [self.source['source_url'].append(link) for link in new_urls]
        self.save(self.source['source_url'], 'pages')
        return self

    def search(self):
        urls = self.urls
        self.search_terms = self.check_split(list(self.search_terms))
        while True:
            try:
                self.driver.get(next(urls))
                search = self.driver.find_element_by_xpath(
                    self.search_xpath)
                while True:
                    try:
                        search_term = next(self.search_terms)
                        search.send_keys(search_term)
                        if not self.error():
                            url = self.driver.current_url
                            self.source.append(url)
                    except StopIteration:
                        break
            except StopIteration:
                break
        return self

    def scrape(self, multi=False):
        predefined = self.predefined_url_list
        urls = self.check_split(predefined) if predefined \
            else self.check_split(self.products)
        while True:
            try:
                self.driver.get(next(urls))
                print(self.driver.current_url)
                self.click_load_more()
                if not multi:
                    self.te_single()
                else:
                    self.te_multi()
            except StopIteration:
                break
        self.save(self.data, 'data')

    def run(self):
        if self.next_xpath:
            self.pagination().scrape()
        elif self.search_xpath:
            self.search().scrape()
        elif self.page_query:
            self.calculate_urls().scrape()
        elif self.predefined_url_list:
            self.scrape(multi=True)
        self.driver.close()

    def run_threads(self):
        jobs = []
        for i in range(self.chunksize):
            self.chunksize = i
            thread = Thread(target=self.run())
            jobs.append(thread)
        for job in jobs:
            job.start()
        for job in jobs:
            job.join()
        # jobs = []
        # for _ in range(self.chunksize):
        #     thread = Thread(target=self.scrape)
        #     jobs.append(thread)
        # for job in jobs:
        #     job.start()
        # for job in jobs:
        #     job.join()

        self.driver.close()
