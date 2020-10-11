import os
import re
import sys
from datetime import datetime
from itertools import product, chain
from time import perf_counter
from time import sleep

import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from utils.utils import get_selectors, concat_keys_values, join_files, check_files


class VenomCrawler:
    # TODO: Check if you can combine starting URL with the url queries
    # TODO: Save Source, Page and Product URL.
    #  Add them to self.data and add method drop(self) to drop unneeded cols
    def __init__(self, name: str, starting_url: str, column_names: list, xpaths: list,
                 next_xpath: str = None, product_xpath: str = None, url_queries: dict = None,
                 page_query: str = None, page_steps: int = None, last_page_xpath: str = None,
                 last_page_arrow: str = None, search_xpath: str = None,
                 search_terms: str = None, load_more: str = None, regex: dict = None,
                 predefined_url_list: list = None, error_xpaths: list = None,
                 chunksize: int = None, chunk: int = None):
        self.start = perf_counter()
        self.name = name
        self.starting_url = starting_url
        if url_queries:
            url_queries = (''.join(chain.from_iterable(e)) for e in
                           product(*map(concat_keys_values, url_queries.items())))
            self.urls = (''.join(url).replace(' ', '%20')
                         for url in product([starting_url], url_queries))
        else:
            self.urls = [starting_url]
        self.selectors = get_selectors(column_names, xpaths)
        self.error_xpaths = error_xpaths
        self.product_xpath = product_xpath
        self.regex = regex
        self.data = {k: [] for k in self.selectors}
        self.source = {'source_url': [], 'page_url': [], 'product_url': []}
        self.chunksize = None if chunksize == 1 else chunksize
        self.chunk = chunk
        self.next_xpath = next_xpath
        self.page_query = page_query
        self.page_steps = page_steps
        self.last_page_xpath = last_page_xpath
        self.search_xpath = search_xpath
        self.last_page_arrow = last_page_arrow
        self.search_terms = search_terms
        self.load_more = load_more
        self.predefined_url_list = predefined_url_list
        self.__driver()
        self.start_time = datetime.now()
        if self.chunksize - 1 == chunk:
            print(f"Initialized: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    def __driver(self):
        self.options = Options()
        self.options.headless = True
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--profile-directory=Default')
        self.options.add_argument("--incognito")
        self.options.add_argument("--disable-plugins-discovery")
        self.options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(os.path.join(os.environ['CHROMEDRIVER']),
                                       options=self.options)
        self.driver.delete_all_cookies()
        self.driver.set_window_size(800, 800)
        self.driver.set_window_position(0, 0)

    def __save(self, data: list or dict, name: str):
        date = self.start_time.strftime('%Y-%m-%d')
        if type(data) == list:
            df = pd.Series(data)
        else:
            df = pd.DataFrame(data)
            columns = ['Date'] + df.columns.to_list()
            df['Date'] = [date] * len(df)
            df = df[columns]
            df.index += 1
        if 'crawlers' not in os.getcwd():
            path = os.path.join(os.getcwd(), 'crawlers', 'data', self.name, name)
        else:
            path = os.path.join(os.getcwd(), 'data', self.name, name)
        if 'data' not in os.listdir(os.getcwd()):
            os.mkdir('data')
        if self.name not in os.listdir(os.path.join(os.getcwd(), 'data')):
            os.mkdir(f'data/{self.name}')
        if name not in os.listdir(os.path.join(os.path.join(os.getcwd(), 'data', self.name))):
            os.mkdir(os.path.join(os.getcwd(), 'data', self.name, name))
        if self.chunksize and name not in ['pages', 'products']:
            df.to_csv(f'{path}/{name} {self.chunk}.csv', encoding='utf-8-sig')
            if check_files(path, name, self.chunksize):
                full_data = join_files(path, name)
                full_data.index += 1
                if f"{self.name} {date}.csv" not in os.listdir(path):
                    full_data.to_csv(f"{path}/{self.name} {date}.csv", encoding='utf-8-sig')
                else:
                    count = len([file for file in os.listdir(path)
                                 if f'{self.name} {date}' in file and file.endswith('.csv')])
                    full_data.to_csv(f"{path}/{self.name} {date} {count}.csv", encoding='utf-8-sig')
        else:
            df.to_csv(f'data/{self.name}/{name}/{self.name} {date}.csv', encoding='utf-8-sig')

    def __check_split(self, url_list: list):
        if self.chunksize and len(url_list) > self.chunksize:
            return np.array_split(url_list, self.chunksize)[self.chunk]
        return url_list

    def __error(self):
        if self.error_xpaths:
            for err in self.error_xpaths:
                try:
                    if self.driver.find_element_by_xpath(err):
                        return True
                except (NoSuchElementException, UnexpectedAlertPresentException):
                    continue

    def __tryexcept(self):
        if self.__error():
            return
        for name, xpath in self.selectors.items():
            if self.regex and name in self.regex.keys():
                pattern = fr"{self.regex[name]}"
                try:
                    element = self.driver.find_element_by_xpath(xpath).text
                    regex = re.findall(pattern, element)[0]
                    element = "".join(regex).strip()
                    self.data[name].append(element)
                except (NoSuchElementException, UnexpectedAlertPresentException):
                    self.data[name].append(np.NaN)
            else:
                try:
                    element = self.driver.find_element_by_xpath(xpath).text
                    self.data[name].append(element)
                except (NoSuchElementException, UnexpectedAlertPresentException):
                    self.data[name].append(np.NaN)

    def __scroll(self, timeout: int = None):
        scroll_pause_time = timeout
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(scroll_pause_time)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def __wait_to_load(self, time, xpath=None):
        if xpath:
            wait = WebDriverWait(self.driver, time)
            wait.until(ec.element_to_be_clickable((By.XPATH, xpath)))
        else:
            self.driver.implicitly_wait(time)

    def __load_more(self):
        if self.load_more:
            while True:
                try:
                    load = self.driver.find_element_by_xpath(self.load_more)
                    load.click()
                    self.__wait_to_load(self.load_more, 10)
                except NoSuchElementException:
                    break

    def __finish(self):
        finish = perf_counter() - self.start
        hours = (finish // 60) // 60
        minutes = (finish // 60) % 60
        seconds = finish % 60
        if check_files(os.path.join(os.getcwd(), 'data', self.name, 'data'), 'data', self.chunksize):
            print(f'\nFinished in {hours} hour(s), {minutes} minute(s) and {seconds} seconds.')
        else:
            print(f"\nFinished {self.name}'s chunk #{self.chunk}")

    def pagination(self):
        urls = self.urls
        for url in urls:
            self.options.add_argument(f"user-agent=")
            self.driver.get(url)
            if not self.__error():
                while True:
                    self.source['source_url'].append(self.driver.current_url)
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
            if not self.__error():
                self.__wait_to_load(20)
                if self.last_page_arrow:
                    self.driver.find_element_by_xpath(self.last_page_arrow).click()
                    sleep(1.5)
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
                sys.stdout.write(f'\r{complete} out of {counter + complete} URLs have been scraped. {counter} left. '
                                 f'Scraped in {(perf_counter() - start):0.2f} seconds')
                counter -= 1
        self.__save(self.source['source_url'], 'pages')
        return self

    def get_services_urls(self):
        if self.product_xpath:
            urls = self.source['source_url'] if len(self.source['source_url']) != 0 else self.urls
            counter = len(urls)
            for source in urls:
                start = perf_counter()
                complete = len(urls) - counter
                self.driver.get(source)
                links = self.driver.find_elements_by_xpath(self.product_xpath)
                products = (url.get_attribute('href') for url in links)
                for url in products:
                    self.source['page_url'].append(source)
                    self.source['product_url'].append(url)
                sys.stdout.write(f'\r{complete} out of {counter + complete} URLs have been scraped. {counter} left. '
                                 f'Scraped in {(perf_counter() - start):0.2f} seconds')
                counter -= 1
            self.__save(self.source['product_url'], 'products')
        else:
            raise AttributeError
        return self

    def search(self):
        urls = self.urls
        search_terms = np.array_split(self.search_terms, self.chunksize)[self.chunk]
        counter = len(urls)
        for url in urls:
            self.driver.get(url)
            search = self.driver.find_element_by_xpath(self.search_xpath)
            for term in search_terms:
                start = perf_counter()
                complete = len(search_terms) - counter
                sys.stdout.flush()
                search.send_keys(term)
                if not self.__error():
                    url = self.driver.current_url
                    self.source['source_url'].append(url)
                    sys.stdout.write(f'\r{complete} out of {counter + complete} URLs have been scraped.'
                                     f' {counter} left. Scraped in {(perf_counter() - start):0.2f} seconds')
                    counter -= 1
        return self

    def scrape(self):
        urls = self.source['product_url']
        predefined = self.predefined_url_list
        urls = self.__check_split(predefined) if self.predefined_url_list\
            else self.__check_split(urls)
        counter = len(urls)
        for url in urls:
            start = perf_counter()
            complete = len(urls) - counter
            sys.stdout.flush()
            self.driver.get(url)
            self.__load_more()
            self.__tryexcept()
            sys.stdout.write(f'\r{complete} out of {counter + complete} URLs '
                             f'have been scraped. {counter} URLs left. '
                             f'Scraped in {(perf_counter() - start):0.2f} seconds')
            counter -= 1
        self.driver.quit()
        self.__save(self.data, 'data')
        self.__finish()
