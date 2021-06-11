import os
import sys
from itertools import product
from time import perf_counter

import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException, \
    InvalidSessionIdException


class Yelp:

    def __init__(self, regions: list, categories: list):
        self.regions = regions
        self.categories = categories
        self.urls = [f'https://www.yelp.com/search?find_desc={category}&find_loc={region}'.replace(' ', '%20')
                     for category, region in product(self.categories, self.regions)]
        self.driver = webdriver.Chrome(os.path.join(os.getcwd(), 'chromedriver.exe'))
        self.pages = {}
        self.data = {"Merchant Name": [], "Merchant Category": [], "Address": [], "Street Name": [], "City": [],
                     "State": [], "Country": [], "Zipcode": [], "Phone no": [], "Source URL": [], "Pricing level": [],
                     "Star rating": [], "Amenities": [], "Hours of Operations": []}

    def pagination(self, url):
        self.driver.get(url)
        while True:
            try:
                self.driver.get(self.driver.current_url)
                if url not in self.pages.keys():
                    self.pages[url] = [self.driver.current_url]
                else:
                    self.pages[url].append(self.driver.current_url)
                next_page = self.driver.find_element_by_xpath(
                    "//div/div/span/a[span[contains(@class, 'chevron-right-v2')]]")
                next_page.click()
            except NoSuchElementException:
                print(f'{len(self.pages[url])} pages have been added for {url}.')
                break
            except UnexpectedAlertPresentException:
                continue
        return self

    def get_page_urls(self):
        for url in self.urls:
            self.pagination(url)
        pd.DataFrame(data=self.pages.items(),
                     columns=['source_url', 'pages']).to_csv('yelp_urls.csv', index=False)
        return self

    def get_services_urls(self):
        urls = pd.read_csv('yelp_urls.csv')
        urls['pages'] = urls['pages'].apply(lambda x: x.replace(']', '').replace('[', '').replace("'", '').split(','))
        urls = urls.explode('pages', ignore_index=True)
        source_url = urls['source_url']
        pages = urls['pages']
        services = pd.DataFrame({'source': [], 'page': [], 'service': []})
        while True:
            try:
                for source, url in zip(source_url, pages):
                    self.driver.get(url)
                    sys.stdout.flush()
                    sys.stdout.write(f'\rServices Count: {len(services)}')
                    service_url = [a_tag.get_attribute('href') for a_tag in
                                   self.driver.find_elements_by_xpath('//div[h4]//span/a')]
                    source_list = source
                    page_list = url
                    df = pd.DataFrame({'source': source_list, 'page': page_list, 'service': service_url})
                    services = pd.concat([services, df], ignore_index=True)
            except (NoSuchElementException, InvalidSessionIdException):
                continue
            finally:
                self.driver.close()
                services.to_csv('services_urls.csv')
            break
        return self

    def scrape(self):
        nan = np.NaN
        urls = pd.read_csv('services_urls.csv', index_col=0)
        counter = len(urls['service'])
        for source, url in zip(urls['source'], urls['service']):
            start = perf_counter()
            while True:
                complete = len(urls['service']) - counter
                sys.stdout.flush()
                self.driver.get(url)
                try:
                    self.driver.find_element_by_xpath(
                        "//h3[contains(.,'the page of results you requested is unavailable.')]")
                    break
                except NoSuchElementException:
                    pass
                try:
                    self.driver.find_element_by_xpath('//span[@class="page-status"]')
                    break
                except NoSuchElementException:
                    pass

                try:
                    merchant_name = self.driver.find_element_by_xpath('//div/h1').text

                    self.data["Merchant Name"].append(merchant_name)
                except NoSuchElementException:
                    break

                merchant_category = self.driver.find_element_by_xpath('//span/span/a').text
                self.data["Merchant Category"].append(merchant_category)

                try:
                    address = self.driver.find_element_by_xpath('//address').text.replace('\n', ' ')
                except NoSuchElementException:
                    address = nan
                self.data["Address"].append(address)

                try:
                    street_name = self.driver.find_element_by_xpath('//address/p').text
                except NoSuchElementException:
                    street_name = nan
                self.data["Street Name"].append(street_name)

                try:
                    country = self.driver.find_element_by_xpath('//address/p[last()]').text
                except NoSuchElementException:
                    country = nan

                try:
                    if country == 'United Kingdom':
                        city = address.split()[len(address.split()) - 5]
                    elif country == 'The Netherlands':
                        city = address.split()[len(address.split()) - 3]
                    else:
                        city = self.driver.find_element_by_xpath('//address/p[last() - 1]').text.split()[1]
                except (NoSuchElementException, IndexError):
                    city = nan
                self.data["City"].append(city)

                self.data["State"].append(nan)
                self.data["Country"].append(country)
                try:
                    if country == 'United Kingdom':
                        zipcode = ' '.join(address.split()[len(address.split()) - 4: len(address.split()) - 2])
                    else:
                        zipcode = self.driver.find_element_by_xpath('//address/p[last() - 1]').text.split()[0]
                except (NoSuchElementException, IndexError):
                    zipcode = nan
                self.data["Zipcode"].append(zipcode)
                try:
                    phone_no = self.driver.find_element_by_xpath(
                        '//section//div[span]/following-sibling::div/p[contains(.,"+")]').text
                except NoSuchElementException:
                    phone_no = nan
                self.data["Phone no"].append(phone_no)

                self.data["Source URL"].append(source)

                try:
                    pricing_level = self.driver.find_element_by_xpath(
                        '//span/span[contains(.,"€") or contains(.,"£")]').text
                except NoSuchElementException:
                    pricing_level = nan
                self.data["Pricing level"].append(pricing_level)

                try:
                    star_rating = self.driver.find_element_by_xpath(
                        '//div[contains(@aria-label, "star rating")]').get_attribute('aria-label')
                except NoSuchElementException:
                    star_rating = nan
                self.data["Star rating"].append(star_rating)

                try:
                    try:
                        self.driver.find_element_by_xpath('//p[contains(.,"More Attribute")]').click()
                    except NoSuchElementException:
                        pass
                    amenities_list = self.driver.find_element_by_xpath(
                        '//div[div[h4[contains(.,"Amenities")]]]/following-sibling::div').text.replace(
                        '\n', ', ').split(', ')
                    checks = ['✔ ' if "normal" in _
                              else '✘ ' for _ in
                              [x.get_attribute('class')
                               for x in self.driver.find_elements_by_xpath(
                                  '//div[div[h4[contains(.,"Amenities")]]]/following-sibling::div'
                                  '/div/div/div/div/div/div[last()]/span')]]
                    amenities = ", ".join([check + amenity for check, amenity in zip(checks, amenities_list)])
                except NoSuchElementException:
                    amenities = nan
                self.data["Amenities"].append(amenities)
                try:
                    hours = self.driver.find_element_by_xpath('//table[contains(.,"Mon")]').text.replace('\n', ' ')
                    hours = hours.replace('pm ', 'pm\n')
                except NoSuchElementException:
                    hours = nan
                self.data['Hours of Operations'].append(hours)
                break
            counter -= 1
            sys.stdout.write(f'\r{complete} out of {counter + complete} URLs have been scraped. {counter} left. '
                             f'{(perf_counter() - start):0.2f}')
        self.driver.close()
        pd.DataFrame(self.data).to_csv('data.csv', encoding='utf-8-sig')
        return self


if __name__ == '__main__':
    start_time = perf_counter()
    countries = ['Germany', 'UK', 'France',
                 'Netherlands', 'Italy', 'Spain']
    search_category = ['Beauty & Spas', 'Jewelry', 'Computer/Software and Media Streaming',
                       'Adult Entertainment', 'Electronics Stores', 'Betting and Casino Gambling']

    yelp = Yelp(countries, search_category)

    yelp.scrape()

    print(f'Finished in {(perf_counter() - start_time) // 60}'
          f' minutes and {round(perf_counter() - start_time, 2) % 60} seconds.')
