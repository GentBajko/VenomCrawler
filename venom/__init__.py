import os
import sys
from itertools import product, chain
from time import perf_counter
from datetime import datetime
import re

import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException

from utils.utils import get_selectors, concat_keys_values, join_files


class Venom:
    # TODO: Load More and Infinite Scroll
    # TODO: Make error checks optional
    def __init__(self, starting_url: str, column_names: list, xpaths: list, error_xpaths: list = None,
                 url_queries: dict = None, product_xpath: str = None, regex: dict = None,
                 splits: int = None, piece: int = None):
        self.starting_url = starting_url
        if url_queries:
            url_queries = (''.join(chain.from_iterable(e)) for e in
                           product(*map(concat_keys_values, url_queries.items())))
            self.urls = (''.join(url).replace(' ', '%20') for url in product([starting_url], url_queries))
        else:
            self.urls = [starting_url]
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(os.path.join(os.environ['CHROMEDRIVER']), options=options)
        self.selectors = get_selectors(column_names, xpaths)
        self.error_xpaths = error_xpaths
        self.product_xpath = product_xpath
        self.regex = regex
        self.pages = []
        self.data = {k: [] for k, _ in self.selectors.items()}
        self.final_urls = {'source_url': [], 'page_url': [], 'product_url': []}
        self.splits = splits
        self.piece = piece
        self.start_time = datetime.now()
        print(f"Initialized: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    def check_split(self):
        if self.splits:
            urls = [url for url in self.urls]
            return np.array_split(urls, self.splits)[self.piece]
        return [url for url in self.urls]

    def error(self):
        if self.error_xpaths:
            for err in self.error_xpaths:
                try:
                    if self.driver.find_element_by_xpath(err):
                        return True
                except (NoSuchElementException, UnexpectedAlertPresentException):
                    continue

    def tryexcept(self, name, xpath):
        if self.regex:
            if name in self.regex.keys():
                pattern = repr(self.regex[name]).replace("'", '')
                try:
                    element = self.driver.find_element_by_xpath(xpath).text
                    regex = re.findall(pattern, element)
                    element = [''.join(x) for x in regex][0].strip()
                    self.data[name].append(element)
                except (NoSuchElementException, UnexpectedAlertPresentException):
                    self.data[name].append(np.NaN)
        else:
            try:
                element = self.driver.find_element_by_xpath(xpath).text
                self.data[name].append(element)
            except (NoSuchElementException, UnexpectedAlertPresentException):
                self.data[name].append(np.NaN)

    def pagination(self, next_xpath: str):
        urls = self.check_split()
        for url in urls:
            self.driver.get(url)
            if not self.error():
                self.pages[url] = []
            while True:
                self.pages[url].append(self.driver.current_url)
                try:
                    next_page = self.driver.find_element_by_xpath(next_xpath)
                    next_page.click()
                except (NoSuchElementException, UnexpectedAlertPresentException):
                    break
        return self

    def calculate_urls(self, page_query: str, page_steps: int, last_page_xpath: str,
                       last_page_arrow: str = None, save_file: bool = True):
        urls = self.check_split()
        counter = len(urls)
        for url in urls:
            start = perf_counter()
            complete = len(urls) - counter
            self.driver.get(url)
            if not self.error():
                if last_page_arrow:
                    self.driver.find_element_by_xpath(last_page_arrow).click()
                last_page = self.driver.find_element_by_xpath(last_page_xpath).text
                last_page = re.search(r'\d+$', last_page).group()
                page_range = [str(i) for i in range(0, int(last_page) * page_steps, page_steps)]
                tuples = product([url], [page_query], page_range)
                new_urls = [''.join(link) for link in tuples]
                [self.pages.append(link) for link in new_urls]
                counter -= 1
                sys.stdout.write(f'\r{complete} out of {counter + complete} URLs have been scraped. {counter} left. '
                                 f'{(perf_counter() - start):0.2f}')
        if save_file:
            series = pd.Series(self.pages)
            website = self.starting_url.split("/")[2]
            if website not in os.listdir(os.getcwd()):
                os.mkdir(website)
            if self.splits:
                if self.splits == self.piece:
                    pd.DataFrame(self.data).to_csv(f'{website}/{website} pages {self.piece}.csv', encoding='utf-8-sig')
                    join_files(website)
                else:
                    series.to_csv(f'{website}/{website} pages {self.piece}.csv', encoding='utf-8-sig')
            else:
                series.to_csv(f'{website}/{website} pages.csv', encoding='utf-8-sig')
        return self

    def get_services_urls(self):
        if self.product_xpath:
            counter = len(list(self.pages))
            for source in self.pages:
                start = perf_counter()
                complete = len(list(self.urls)) - counter
                self.driver.get(source)
                urls = self.driver.find_elements_by_xpath(self.product_xpath)
                products = (url.text for url in urls)
                for url in products:
                    self.final_urls['page_url'].append(source)
                    self.final_urls['product_url'].append(url)
                counter -= 1
                sys.stdout.write(f'\r{complete} out of {counter + complete} URLs have been scraped. {counter} left. '
                                 f'{(perf_counter() - start):0.2f}')
        else:
            raise AttributeError
        return self

    def search(self, search_xpath, search_terms):
        urls = self.check_split()
        counter = len(urls)
        self.driver.get(*self.urls)
        search = self.driver.find_element_by_xpath(search_xpath)
        for term in search_terms:
            start = perf_counter()
            complete = len(search_terms) - counter
            sys.stdout.flush()
            search.send_keys(term)
            if not self.error():
                url = self.driver.current_url
                self.pages.append(url)
                counter -= 1
                sys.stdout.write(f'\r{complete} out of {counter + complete} URLs have been scraped. {counter} left. '
                                 f'{(perf_counter() - start):0.2f}')
        return self

    def scrape(self, predefined_url_list: list = None, load_more: str = None):
        if len(list(self.urls)) > 1:
            if self.splits:
                if predefined_url_list:
                    urls = np.array_split(predefined_url_list, self.splits)[self.piece]
                else:
                    urls = np.array_split(self.final_urls, self.splits)[self.piece]
            else:
                urls = predefined_url_list if predefined_url_list else self.final_urls
        else:
            urls = self.pages
        counter = len(list(urls))
        for url in urls:
            start = perf_counter()
            complete = len(list(urls)) - counter
            sys.stdout.flush()
            if load_more:
                load = self.driver.find_element_by_xpath(load_more)
                while load:
                    load.click()
                    # TODO: Check if sleep is needed
            self.driver.get(url)
            if not self.error():
                for column, selector in self.selectors.items():
                    self.tryexcept(column, selector)
            counter -= 1
            sys.stdout.write(f'\r{complete} out of {counter + complete} URLs have been scraped. {counter} left. '
                             f'{(perf_counter() - start):0.2f}')
        self.driver.close()
        website = self.starting_url.split("/")[2]
        if website not in os.listdir(os.getcwd()):
            os.mkdir(website)
        if self.splits:
            if self.splits == self.piece:
                pd.DataFrame(self.data).to_csv(f'{website}/{website} {self.piece}.csv', encoding='utf-8-sig')
                join_files(website)
            else:
                pd.DataFrame(self.data).to_csv(f'{website}/{website} {self.piece}.csv', encoding='utf-8-sig')
        else:
            date = datetime.now().strftime('%Y-%m-%d')
            pd.DataFrame(self.data).to_csv(f'{website}/{website} {date}.csv', encoding='utf-8-sig')
        print(f"\n\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        return self
