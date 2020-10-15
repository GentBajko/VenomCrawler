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


class Composer:
    def __init__(self, name: str, starting_url: str,
                 column_names: list, xpaths: list,
                 next_xpath: str = None, product_xpath: str = None,
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
        self.start = perf_counter()
        self.name = name
        self.starting_url = check_url_prefix(starting_url)
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
        self.source = []
        self.pages = []
        self.products = []
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
        self.start_driver()
        self.start_time = datetime.now()
        self.useragent = UserAgent().random
        if self.chunksize - 1 == chunk:
            print(f"Initialized: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    def start_driver(self):
        self.options = ChromeOptions()
        self.options.headless = True
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--profile-directory=Default')
        self.options.add_argument("--incognito")
        self.options.add_argument("--disable-plugins-discovery")
        self.driver = Chrome(options=self.options)
        self.driver.delete_all_cookies()
        self.driver.set_window_size(800, 800)
        self.driver.set_window_position(0, 0)

    def save(self, data: list or dict, name: str):
        date = self.start_time.strftime('%Y-%m-%d')
        if type(data) == list:
            df = pd.Series(data)
        else:
            df = pd.DataFrame(data)
            columns = ['Date'] + df.columns.to_list()
            df['Date'] = [date] * len(df)
            df = df[columns]
            df.index += 1
        if 'crawlers' not in os.listdir('Venom'):
            path = os.path.join('Venom', 'crawlers', 'data', self.name, name)
        else:
            path = os.path.join(os.getcwd(), 'data', self.name, name)
        os.makedirs(path, exist_ok=True)
        if self.chunksize and name not in ['pages', 'products']:
            df.to_csv(f'{path}/{name} {self.chunk}.csv', encoding='utf-8-sig')
            if check_files(path, name, self.chunksize):
                full_data = join_files(path, name)
                if f"{self.name} {date}.csv" not in os.listdir(path):
                    full_data.to_csv(f"{path}/{self.name} {date}.csv", encoding='utf-8-sig')
                else:
                    count = len([file for file in os.listdir(path)
                                 if f'{self.name} {date}' in file and file.endswith('.csv')])
                    full_data.to_csv(f"{path}/{self.name} {date} {count}.csv", encoding='utf-8-sig')
        else:
            df.to_csv(f'data/{self.name}/{name}/{self.name} {date}.csv', encoding='utf-8-sig')

    def check_split(self, url_list: list):
        if self.chunksize and len(url_list) > self.chunksize:
            return np.array_split(url_list, self.chunksize)[self.chunk]
        return iter(url_list)

    def error(self):
        if self.error_xpaths:
            for err in self.error_xpaths:
                try:
                    if self.driver.find_element_by_xpath(err):
                        return True
                except (NoSuchElementException, UnexpectedAlertPresentException):
                    continue

    def tryexcept(self):
        if self.error():
            return
        for name, xpath in self.selectors.items():
            if self.regex and name in self.regex.keys():
                pattern = fr"{self.regex[name]}"
                try:
                    element = find_regex(pattern,
                                         self.driver.find_element_by_xpath(xpath).text)
                    self.data[name].append(element)
                except (NoSuchElementException, UnexpectedAlertPresentException):
                    self.data[name].append(np.NaN)
            else:
                try:
                    element = self.driver.find_element_by_xpath(xpath).text
                    self.data[name].append(element)
                except (NoSuchElementException, UnexpectedAlertPresentException):
                    self.data[name].append(np.NaN)

    def scroll(self, timeout: int = None):
        scroll_pause_time = timeout
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(scroll_pause_time)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def wait_to_load(self, time, xpath=None):
        if xpath:
            wait = WebDriverWait(self.driver, time)
            wait.until(ec.element_to_be_clickable((By.XPATH, xpath)))
        else:
            self.driver.implicitly_wait(time)

    def click_last_page_arrow(self):
        if self.last_page_arrow:
            self.driver.find_element_by_xpath(self.last_page_arrow).click()
            sleep(1.5)

    def load_more(self):
        if self.load_more:
            while True:
                try:
                    load = self.driver.find_element_by_xpath(self.load_more)
                    load.click()
                    self.wait_to_load(self.load_more, 10)
                except NoSuchElementException:
                    break

    def finish(self):
        finish = perf_counter() - self.start
        hours = (finish // 60) // 60
        minutes = (finish // 60) % 60
        seconds = finish % 60
        if check_files(os.path.join(os.getcwd(), 'data', self.name, 'data'), 'data', self.chunksize):
            print(f'\nFinished in {hours} hour(s), {minutes} minute(s) and {seconds} seconds.')
        else:
            print(f"\nFinished {self.name}'s chunk #{self.chunk}")

    def get_services(self, url):
        if self.product_xpath:
            links = self.driver.find_elements_by_xpath(self.product_xpath)
            products = (source.get_attribute('href') for source in links)
            for url in products:
                self.pages.append(url)
                self.products.append(url)
