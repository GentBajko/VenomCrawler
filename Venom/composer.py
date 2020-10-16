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
import threading
import undetected_chromedriver as uc
uc.install()
from selenium.webdriver import Chrome, ChromeOptions
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from Venom.utils.utils import get_selectors, concat_keys_values, join_files,\
    check_files, check_url_prefix, add_date, get_path
from Venom.utils.actions import find_regex, get_useragent, save_data


class Composer:
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
        self.options.add_argument('--ignore-certificate-errors')
        get_useragent(self.options)
        self.driver = Chrome(options=self.options)
        self.driver.delete_all_cookies()
        self.driver.set_window_size(800, 800)
        self.driver.set_window_position(0, 0)

    def save(self, data: list or dict, name: str):
        date = self.start_time.strftime('%Y-%m-%d')
        df = add_date(data, date)
        path = get_path(self.name, name)
        filename = f"{self.name} {date}.csv"
        if self.chunksize and name not in ['pages', 'products']:
            save_data(self.name, name, df, self.chunksize, self.chunk, path, date, filename)
        else:
            df.to_csv(f'data/{self.name}/{name}/{filename}', encoding='utf-8-sig')

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

    def click_load_more(self):
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

    def get_services(self, url):
        if self.product_xpath:
            links = self.driver.find_elements_by_xpath(self.product_xpath)
            products = (source.get_attribute('href') for source in links)
            for link in products:
                self.pages.append(url)
                self.products.append(link)

    def find_elements(self, xpath, _from: int = 0, to: int = None):
        return self.driver.find_elements_by_xpath(xpath)[_from:to]

    def find_by_text(self, text: str, _from: int = 0, to: int = None):
        return self.driver.find_elements_by_xpath(f"//*[contains(text(), {text})]")[_from:to]

    def scrape(self):
        predefined = self.predefined_url_list
        urls = self.check_split(predefined) if self.predefined_url_list \
            else self.check_split(self.products)
        while True:
            try:
                self.driver.get(next(urls))
                self.click_load_more()
                self.tryexcept()
            except StopIteration:
                self.driver.quit()
                break
        self.save(self.data, 'data')

    def __run(self):
        pass

    def start_threads(self):
        jobs = []
        for _ in range(self.chunksize):
            thread = threading.Thread(target=self.__run())
            jobs.append(thread)
        for job in jobs:
            job.start()
        for job in jobs:
            job.join()
        self.finish()