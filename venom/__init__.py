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

from utils import get_selectors, concat_keys_values, join_files, check_files
import pickle
from time import sleep


class Venom:
    # TODO: Check if you can combine starting URL with the url queries
    starting_url: str
    column_names: list
    xpaths: list

    product_xpath: str = None

    next_xpath: str

    url_queries: dict = None
    page_query: str
    page_steps: int
    last_page_xpath: str
    last_page_arrow: str = None

    search_xpath: str = None
    search_terms: str = None

    load_more: str = None

    regex: dict = None
    chunksize: int = None
    predefined_url_list: list = None
    error_xpaths: list = None
    save_file: bool = True

    def __init__(self, name: str, chunksize: int = None, chunk: int = None):
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
        # Initialize a split session if conditions are True or values are not None
        self.chunksize = int(sys.argv[1]) if len(sys.argv) > 1 else chunksize
        self.chunk = int(sys.argv[2]) if len(sys.argv) > 1 else chunk
        self.start_time = datetime.now()
        print(f"Initialized: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    def init_driver(self, hidden=True):
        options = Options()
        # Sets the webdriver's visibility as referenced in the argument
        options.headless = hidden
        # Opens the webdriver. Make sure to create an enviroment variable CHROMEDRIVER with it's path
        self.driver = webdriver.Chrome(os.path.join(os.environ['CHROMEDRIVER']), options=options)
        return self

    def save(self, data: list or dict, name: str):
        # Checks if there was a request to save the file. If not, returns None
        if not self.save_file:
            return
        # Gets current date in the Year-Month-Day (2020-06-20) string format
        date = self.start_time.strftime('%Y-%m-%d')
        # Converts the URL into a pandas series
        df = pd.Series(data) if type(data) == list else pd.DataFrame(data)
        # Grabs the domain of the website being scraped (venomcrawler.com)
        website = self.starting_url.split("/")[2]
        # If a folder with the domain name does not exist, it is created
        if website not in os.listdir(os.getcwd()):
            os.mkdir(website)
        # If a folder with the file type name does not exist, it is created
        if name not in os.listdir(os.path.join(os.getcwd(), website)):
            os.mkdir(os.path.join(os.getcwd(), website, name))
        # Checks is list splitting is enabled
        if self.chunksize:
            if check_files(self.chunksize, website, name):
                # Exports the dataframe into CSV
                df.to_csv(f'{website}/{name}/{website} {name} {self.chunk}.csv',
                          encoding='utf-8-sig')
                # Joins all CSVs created during this split session
                join_files(website, name).to_csv(f"{website} {date}")
            else:
                # If this instance isn't the last one to finish,
                # it simply exports this chunk's data into a csv
                df.to_csv(f'{website}/{name}/{website} {name} {self.chunk}.csv', encoding='utf-8-sig')
        else:
            # If not a split session, export all the data into a csv
            # with today's date in the name
            df.to_csv(f'{website}/{name}/{website} {name} {date}.csv', encoding='utf-8-sig')

    def check_split(self, url_list: list):
        # Checks if instance was asked to split the list into pieces.
        # If the length of the list is lower than the split request,
        # the request is ignored, so not to cause conflict.
        if self.chunksize and len(url_list) > self.chunksize:
            # Returns the requested piece of the split list
            return np.array_split(url_list, self.chunksize)[self.chunk]
        # If no split was requested, it returns the normal list
        return url_list

    def error(self):
        # Check if there are any error xpaths to search
        if self.error_xpaths:
            # Iterate the error xpath list
            for err in self.error_xpaths:
                try:
                    # If the error is found, returns True
                    if self.driver.find_element_by_xpath(err):
                        return True
                # If no errors were found, returns False
                except (NoSuchElementException, UnexpectedAlertPresentException):
                    continue

    def tryexcept(self, name, xpath):
        # Check if the column name has a regex pattern
        if self.regex and name in self.regex.keys():
            # Create a raw string version of the regex pattern
            pattern = fr"{self.regex[name]}"
            try:
                # Get the element's text
                element = self.driver.find_element_by_xpath(xpath).text
                # Search the text for the pattern
                regex = re.findall(pattern, element)[0].strip()
                # Add the pattern to the data
                self.data[name].append(regex)
            # If the element isn't found, append NaN
            except (NoSuchElementException, UnexpectedAlertPresentException):
                self.data[name].append(np.NaN)
        else:
            # If there is no regex pattern for the column, the whole element is added
            try:
                element = self.driver.find_element_by_xpath(xpath).text
                self.data[name].append(element)
            except (NoSuchElementException, UnexpectedAlertPresentException):
                self.data[name].append(np.NaN)

    def scroll(self, timeout: int = None):
        # Set sleep time
        scroll_pause_time = timeout
        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            sleep(scroll_pause_time)
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            # If heights are the same it will exit the function
            if new_height == last_height:
                break
            # Set the old height value to the new one
            last_height = new_height

    def pagination(self):
        # Checks if the session is a split one. Gets URL list accordingly
        urls = self.check_split(self.urls)
        # Iteraters over the URLs
        for url in urls:
            # Open the current iteration's URL on chromedriver
            self.driver.get(url)
            # Checks to see if this URL is displaying any of the listed errors
            if not self.error():
                # If there are errors, add an empty list instead of the url
                self.pages[url] = []
            # Infinite loop, breaks when there is no more Next button on the page
            while True:
                # Adds the browser's current URL into the current iteration URLs list
                self.pages[url].append(self.driver.current_url)
                try:
                    # If there is a Next button, it clicks it
                    next_page = self.driver.find_element_by_xpath(self.next_xpath)
                    next_page.click()
                # Else, it ends the loop
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
        # TODO: if split session, urls = self.pages[self.chunk] ????????
        if self.product_xpath:
            urls = self.pages
            counter = len(urls)
            for source in urls:
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
        urls = self.urls
        # Initiate counter
        counter = len(urls)
        for url in urls:
            # Open URL
            self.driver.get(url)
            # Finds the search bar
            search = self.driver.find_element_by_xpath(self.search_xpath)
            # Iterates over the search terms
            for term in self.search_terms:
                # Starts timer
                start = perf_counter()
                # Number of URLs scraped: Lenth of total URLs - current counter
                complete = len(self.search_terms) - counter
                sys.stdout.flush()
                # Type the search term on the search bar
                search.send_keys(term)
                # Check to see is there are not errors
                if not self.error():
                    # Add the current URL to the pages list
                    url = self.driver.current_url
                    self.pages.append(url)
                    # Decrease counter by 1
                    counter -= 1
                    sys.stdout.write(f'\r{complete} out of {counter + complete} URLs have been scraped.'
                                     f' {counter} left. {(perf_counter() - start):0.2f}')
        return self

    def scrape(self):
        urls = self.final_urls['product_url']
        predefined = self.predefined_url_list
        # Splits urls if split session. Predefined URLs take precedence.
        urls = self.check_split(predefined) if self.predefined_url_list else self.check_split(urls)
        # Initializes counter
        counter = len(urls)
        # Iterates over the URLs
        for url in urls:
            # Starts timer
            start = perf_counter()
            # Number of URLs scraped
            complete = len(urls) - counter
            sys.stdout.flush()
            # Open URL
            self.driver.get(url)
            # Check if website has a load more button
            if self.load_more:
                while True:
                    try:
                        # Click load more
                        load = self.driver.find_element_by_xpath(self.load_more)
                        load.click()
                        # Wait 1.3 seconds
                        sleep(1.3)
                    except NoSuchElementException:
                        break
            # Check if page has any errors
            if not self.error():
                # Iterate over the columns and xpaths
                for column, selector in self.selectors.items():
                    # Find and add the elements to the list
                    self.tryexcept(column, selector)
            # Decrease counter by one
            counter -= 1
            sys.stdout.write(f'\r{complete} out of {counter + complete} URLs have been scraped. {counter} left. '
                             f'{(perf_counter() - start):0.2f}')
        # Close the webdriver
        self.driver.close()
        self.save_file = True
        self.save(self.data, 'data')
        print(f"\n\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        return self

    def serialize(self):
        with open(f"{self.name}.pkl", 'wb') as f:
            pickle.dump(self, f)
