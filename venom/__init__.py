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

from utils import get_selectors, concat_keys_values, join_files
import pickle
from time import sleep


class Venom:
    starting_url: str
    column_names: list
    xpaths: list
    error_xpaths: list = None
    url_queries: dict = None
    product_xpath: str = None
    regex: dict = None
    next_xpath: str
    chunksize: int = None
    page_query: str
    page_steps: int
    last_page_xpath: str
    last_page_arrow: str = None
    search_xpath: str = None
    search_terms: str = None
    predefined_url_list: list = None
    load_more: str = None
    save_file: bool = True

    def __init__(self, name: str):
        self.name = name
        if self.url_queries:
            url_queries = (''.join(chain.from_iterable(e)) for e in
                           product(*map(concat_keys_values, self.url_queries.items())))
            self.urls = [''.join(url).replace(' ', '%20') for url in product([self.starting_url], url_queries)]
        else:
            self.urls = [self.starting_url]
        self.driver = None
        self.selectors = get_selectors(self.column_names, self.xpaths)
        self.pages = []
        self.data = {k: [] for k in self.selectors}
        self.final_urls = {'source_url': [], 'page_url': [], 'product_url': []}
        if len(sys.argv) > 1:
            self.chunksize = int(sys.argv[1])
            self.chunk = int(sys.argv[2])
            print(self.chunksize, self.chunk)
        self.start_time = datetime.now()
        print(f"Initialized: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    def init_driver(self, hidden=True):
        options = Options()
        options.headless = hidden
        self.driver = webdriver.Chrome(os.path.join(os.environ['CHROMEDRIVER']), options=options)
        return self

    def save(self, url_list: list, name: str):
        if not self.save_file:
            return
        date = datetime.now().strftime('%Y-%m-%d')
        series = pd.Series(url_list)
        website = self.starting_url.split("/")[2]
        if website not in os.listdir(os.getcwd()):
            os.mkdir(website)
        if self.chunksize:
            if self.chunksize == self.chunk:
                pd.DataFrame(self.data).to_csv(f'{website}/{website} {name} {self.chunk}.csv', encoding='utf-8-sig')
                join_files(website)
            else:
                series.to_csv(f'{website}/{website} {name} {self.chunk}.csv', encoding='utf-8-sig')
        else:
            series.to_csv(f'{website}/{website} {name} {date}.csv', encoding='utf-8-sig')

    def check_split(self, url_list: list):
        if self.chunksize:
            return np.array_split(url_list, self.chunksize)[self.chunk]
        return url_list

    def error(self):
        if self.error_xpaths:
            for err in self.error_xpaths:
                try:
                    if self.driver.find_element_by_xpath(err):
                        return True
                except (NoSuchElementException, UnexpectedAlertPresentException):
                    continue

    def tryexcept(self, name, xpath):
        if self.regex and name in self.regex.keys():
            pattern = fr"{self.regex[name]}"
            try:
                element = self.driver.find_element_by_xpath(xpath).text
                regex = re.findall(pattern, element)[0].strip()
                self.data[name].append(regex)
            except (NoSuchElementException, UnexpectedAlertPresentException):
                self.data[name].append(np.NaN)
        else:
            try:
                element = self.driver.find_element_by_xpath(xpath).text
                self.data[name].append(element)
            except (NoSuchElementException, UnexpectedAlertPresentException):
                self.data[name].append(np.NaN)

    def pagination(self):
        urls = self.check_split(self.urls)
        for url in urls:
            self.driver.get(url)
            if not self.error():
                self.pages[url] = []
            while True:
                self.pages[url].append(self.driver.current_url)
                try:
                    next_page = self.driver.find_element_by_xpath(self.next_xpath)
                    next_page.click()
                except (NoSuchElementException, UnexpectedAlertPresentException):
                    break
        return self

    def calculate_urls(self):
        urls = self.urls
        counter = len(urls)
        for url in urls:
            start = perf_counter()
            complete = len(urls) - counter
            self.driver.get(url)
            if not self.error():
                if self.last_page_arrow:
                    self.driver.find_element_by_xpath(self.last_page_arrow).click()
                    sleep(1.5)
                last_page = self.driver.find_element_by_xpath(self.last_page_xpath).text
                last_page = re.search(r'\d+$', last_page).group()
                page_range = [str(i) for i in
                              range(0, int(last_page) * self.page_steps, self.page_steps)]
                tuples = product([url], [self.page_query], page_range)
                new_urls = [''.join(link) for link in tuples]
                [self.pages.append(link) for link in new_urls]
                counter -= 1
                sys.stdout.write(f'\r{complete} out of {counter + complete} URLs have been scraped. {counter} left. '
                                 f'{(perf_counter() - start):0.2f}')
        self.save(self.pages, 'pages')
        return self

    def get_services_urls(self):
        if self.product_xpath:
            urls = self.check_split(self.pages)
            counter = len(urls)
            for source in urls[:1]:
                start = perf_counter()
                complete = len(self.pages) - counter
                self.driver.get(source)
                urls = self.driver.find_elements_by_xpath(self.product_xpath)
                products = (url.get_attribute('href') for url in urls)
                for url in products:
                    self.final_urls['page_url'].append(source)
                    self.final_urls['product_url'].append(url)
                counter -= 1
                sys.stdout.write(f'\r{complete} out of {counter + complete} URLs have been scraped. {counter} left. '
                                 f'{(perf_counter() - start):0.2f}')

            self.save(self.final_urls['product_url'], 'products')
        else:
            raise AttributeError
        return self

    def search(self):
        urls = self.check_split(self.urls)
        counter = len(urls)
        self.driver.get(*self.urls)
        search = self.driver.find_element_by_xpath(self.search_xpath)
        for term in self.search_terms:
            start = perf_counter()
            complete = len(self.search_terms) - counter
            sys.stdout.flush()
            search.send_keys(term)
            if not self.error():
                url = self.driver.current_url
                self.pages.append(url)
                counter -= 1
                sys.stdout.write(f'\r{complete} out of {counter + complete} URLs have been scraped. {counter} left. '
                                 f'{(perf_counter() - start):0.2f}')
        return self

    def scrape(self):
        urls = self.final_urls['product_url']
        predefined = self.predefined_url_list
        urls = self.check_split(predefined) if self.predefined_url_list else self.check_split(urls)
        counter = len(urls)
        for url in urls[:5]:
            start = perf_counter()
            complete = len(urls) - counter
            sys.stdout.flush()
            if self.load_more:
                while True:
                    try:
                        load = self.driver.find_element_by_xpath(self.load_more)
                        load.click()
                        sleep(1.3)
                    except NoSuchElementException:
                        break
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
        if self.chunksize:
            if self.chunksize == self.chunk:
                pd.DataFrame(self.data).to_csv(f'{website}/{website} {self.chunk}.csv', encoding='utf-8-sig')
                join_files(website)
            else:
                pd.DataFrame(self.data).to_csv(f'{website}/{website} {self.chunk}.csv', encoding='utf-8-sig')
        else:
            date = datetime.now().strftime('%Y-%m-%d')
            df = pd.DataFrame.from_dict(self.data, orient='index').T
            df.to_csv(f'{website}/{website} {date}.csv', encoding='utf-8-sig')
        print(f"\n\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        return self

    def serialize(self):
        with open(f"{self.name}.pkl", 'wb') as f:
            pickle.dump(self, f)
