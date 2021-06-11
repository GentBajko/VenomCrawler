import asyncio
import re
from random import randint
from time import perf_counter

import numpy as np
import pandas as pd
import urllib3
from requests.exceptions import ProxyError
from requests_html import AsyncHTMLSession

from proxies import nordvpn
from utils import selectors, split_urls

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Scraper:

    # TODO: Fix Zipcode
    # TODO: Append States if "country": df[country == country].append
    # TODO: Append starting url

    def __init__(self, name: str, element_paths: dict, url_list: pd.DataFrame = None,
                 proxy: bool = True, batch_size: int = 8, render: bool = False):
        self.name = name
        self.selectors = element_paths
        self.urls = url_list
        self.proxy = proxy
        self.batch_size = batch_size
        self.render = render
        self.asession = AsyncHTMLSession()
        self.data = {key: [] for key in selectors}
        self.finished = 0

    async def scrape(self, url):
        if self.proxy:
            while True:
                proxy = next(nordvpn)
                try:
                    self.asession.proxies = {'http': f"amichaluk%40hotmail.com:Adodasm33@{proxy}.nordvpn.com",
                                             'https': f"amichaluk%40hotmail.com:Adodasm33@{proxy}.nordvpn.com"}
                    r = await self.asession.get(url, verify=False)
                    print(f'{url} connected to {proxy}.nordvpn.com')
                    break
                except ProxyError:
                    pass
        else:
            await asyncio.sleep(randint(0, 1))
            r = await self.asession.get(url)
        if self.render:
            await r.html.arender(retries=3, timeout=70)
        for k, v in self.selectors.items():
            if v:
                try:
                    try:
                        el = r.html.xpath(v, first=True).text
                        if el == 'Yelp':
                            print('Probably Blocked')
                            self.proxy = True
                        if bool(re.search(r'(€+[A-z]+|£+[A-z]+)', el)):
                            el = np.NaN
                        if k == 'Zipcode':
                            el = " ".join(r.html.xpath(v, first=True).text.split()[1:])
                        self.data[k].append(el)
                    except AttributeError:
                        el = r.html.xpath(v)[0]
                        self.data[k].append(el)
                except IndexError:
                    self.data[k].append(np.NaN)

    async def spider(self):
        start = perf_counter()
        single_url_list = list(self.urls)
        for urls in split_urls(single_url_list, self.batch_size):
            await asyncio.wait([self.scrape(url) for url in urls])
            finish = perf_counter() - start
            self.finished += len(urls)
            print(f'\rFinished first spider {len(urls)} in {finish:0.3f}. {(finish / len(urls)):0.3f}')

    async def first_spider(self):
        start = perf_counter()
        first_url_list = np.array_split(list(self.urls), 2)[0]
        for urls in split_urls(first_url_list, self.batch_size):
            await asyncio.wait([self.scrape(url) for url in urls])
            finish = perf_counter() - start
            self.finished += len(urls)
            print(f'\rFinished first spider {len(urls)} in {finish:0.3f}. {(finish / len(urls)):0.3f}')

    async def second_spider(self):
        start = perf_counter()
        second_url_list = np.array_split(list(self.urls), 2)[1]
        for urls in split_urls(second_url_list, self.batch_size):
            await asyncio.wait([self.scrape(url) for url in urls])
            finish = perf_counter() - start
            self.finished += len(urls)
            print(f'Finished second spider {len(urls)} in {finish:0.3f}. {(finish / len(urls)):0.3f}')

    def start(self, mode: str = 'multi'):
        if mode.lower() == 'multi':
            self.asession.run(self.first_spider, self.second_spider)
        elif mode.lower() == 'single':
            self.asession.run(self.spider)
        else:
            raise AttributeError
        return self

    def additional_data(self):
        # TODO: Dict with {str: tuple} where str is the data key and the tuple shows what it is connected with
        self.data['Merchant Name'] = [x.split(' - ')[0] for x in self.data['Title']]
        self.data['Merchant Category'] = [x.split(' - ')[2] for x in self.data['Title']]
        self.data['Address'] = [x.split(' - ')[3] for x in self.data['Title']]
        self.data['Street Name'] = [x.split(', ')[0] if x != 'Phone Number' else np.NaN
                                    for x in self.data['Address']]
        self.data['City'] = [', '.join(x.split(', ')[1:3]) if x != 'Phone Number' else np.NaN
                             for x in self.data['Address']]
        self.data['Country'] = [x.split(', ')[3] if x != 'Phone Number' else np.NaN
                                for x in self.data['Address']]
        self.data['State'] = self.data['Country']
        return self

    def write(self, file_type):
        df = pd.DataFrame(self.data)
        if file_type.lower() == 'csv':
            df.to_csv(f'{self.name}_data.csv', encoding='utf-8-sig')
        if file_type.lower() == 'pickle':
            df.to_pickle(f'{self.name}_data.pkl')
        if file_type.lower() in ['excel', 'xlsx]']:
            df.to_excel(f'{self.name}_data.xlsx', encoding='utf-8-sig')


if __name__ == '__main__':
    start_time = perf_counter()

    yelp = Scraper('yelp', selectors, pd.read_csv('services_urls.csv')['service'].tolist()[0:40],
                   proxy=False, batch_size=5)

    yelp.start('Multi')
    # df = pd.DataFrame(yelp.data)
    print(yelp.data)

    finished = perf_counter() - start_time
    print(f'Ran {yelp.finished} in {finished:0.3f}. {finished / yelp.finished}')
