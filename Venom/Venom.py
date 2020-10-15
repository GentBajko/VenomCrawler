import os
import re
import sys
from datetime import datetime
from itertools import product, chain
from time import perf_counter
from time import sleep

from fake_useragent import UserAgent
import numpy as np
import pandas as pd
import undetected_chromedriver as uc
uc.install()
from selenium.webdriver import Chrome, ChromeOptions
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from Venom.utils.utils import get_selectors, concat_keys_values, join_files, check_files, check_url_prefix
from Venom.utils.actions import find_elements, find_regex, find_elements_by_text, get_useragent
import threading
from Venom.composer import Composer


class VenomPaginate(Composer):
    def __init__(self, name: str, starting_url: str,
                 column_names: list, xpaths: list,
                 next_xpath: str = None, product_xpath: str = None,
                 chunksize: int = None, chunk: int = None):
        super().__init__(name, starting_url, column_names, xpaths,
                         next_xpath, product_xpath, chunksize, chunk)

    def pagination(self):
        self.urls = iter(self.urls)
        while True:
            try:
                url = next(self.urls)
                self.driver.get(url)
                if not self.error():
                    while True:
                        self.source.append(self.driver.current_url)
                        self.get_services(self.driver.current_url)
                        try:
                            self.driver.find_element_by_xpath(self.next_xpath).click()
                        except (NoSuchElementException, UnexpectedAlertPresentException):
                            break
            except StopIteration:
                break
        self.save(self.source, 'pages')
        self.save(self.products, 'products')
        return self

    def calculate_urls(self):
        self.urls = iter(self.urls)
        while True:
            try:
                url = next(self.urls)
                # start = perf_counter()
                self.driver.get(url)
                if not self.error():
                    self.wait_to_load(20)
                    self.click_last_page_arrow()
                    last_page = self.driver.find_element_by_xpath(self.last_page_xpath).text
                    last_page = re.search(r'\d+$', last_page).group()
                    if self.page_steps == 1:
                        page_range = [str(i) for i in
                                      range(1, (int(last_page) * self.page_steps) + 1,
                                            self.page_steps)]
                    else:
                        page_range = [str(i) for i in
                                      range(0, int(last_page) * self.page_steps, self.page_steps)]
                    tuples = product([url], [self.page_query], page_range)
                    new_urls = [''.join(link) for link in tuples]
                    [self.source.append(link) for link in new_urls]
                    # sys.stdout.write(f'Scraped in {(perf_counter() - start):0.2f} seconds')
            except StopIteration:
                break
        self.save(self.source, 'pages')
        self.save(self.products, 'products')
        return self

    def get_services_urls(self):
        if self.product_xpath:
            url_list = self.source if len(self.source) != 0 else self.urls
            urls = iter(url_list)
            # counter, length = len(url_list), len(url_list)
            while True:
                try:
                    source = next(urls)
                    # start = perf_counter()
                    # complete = length - counter
                    self.driver.get(source)
                    links = self.driver.find_elements_by_xpath(self.product_xpath)
                    products = (source.get_attribute('href') for source in links)
                    for url in products:
                        self.pages.append(source)
                        self.products.append(url)
                    # sys.stdout.write(f'\r{complete} out of {counter + complete} '
                    #                  f'URLs have been scraped. {counter} left. '
                    #                  f'Scraped in {(perf_counter() - start):0.2f} seconds')
                    # counter -= 1
                except StopIteration:
                    break
            self.save(self.products, 'products')
        else:
            raise AttributeError(
                "Product Xpaths have not been declared"
            )
        return self

    def search(self):
        urls = self.urls
        search_terms = np.array_split(self.search_terms, self.chunksize)[self.chunk]
        # counter, length = len(urls), len(urls)
        while True:
            try:
                url = next(urls)
                self.driver.get(next(url))
                search = self.driver.find_element_by_xpath(self.search_xpath)
                self.search_terms = iter(self.search_terms)
                while True:
                    try:
                        search_term = next(self.search_terms)
                        # start = perf_counter()
                        # sys.stdout.flush()
                        # complete = len(search_terms) - counter
                        search.send_keys(search_term)
                        if not self.error():
                            url = self.driver.current_url
                            self.source.append(url)
                            # sys.stdout.write(f'\r{complete} out of {counter + complete} '
                            #                  f'URLs have been scraped.'
                            #                  f' {counter} left. Scraped in '
                            #                  f'{(perf_counter() - start):0.2f} seconds')
                            # counter -= 1
                    except StopIteration:
                        break
            except StopIteration:
                break
        return self

    def scrape(self):
        predefined = self.predefined_url_list
        urls = self.check_split(predefined) if self.predefined_url_list\
            else self.check_split(self.products)
        # counter, length = len(urls), len(urls)
        while True:
            try:
                # start = perf_counter()
                # sys.stdout.flush()
                # complete = length - counter
                self.driver.get(next(urls))
                self.load_more()
                self.tryexcept()
                # sys.stdout.write(f'\r{complete} out of {counter + complete} URLs '
                #                  f'have been scraped. {counter} URLs left. '
                #                  f'Scraped in {(perf_counter() - start):0.2f} seconds')
                # counter -= 1
            except StopIteration:
                self.driver.quit()
                break
        self.save(self.data, 'data')
        self.finish()


if __name__ == '__main__':
    pass
