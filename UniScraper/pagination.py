import asyncio
import re
from itertools import product, chain
from random import randint
from time import perf_counter, sleep

import numpy as np
import pandas as pd
import urllib3
from requests.exceptions import ProxyError
from requests_html import AsyncHTMLSession

from proxies import get_nord
from utils import concat_keys_values, categories, locations, split_urls

# TODO: asyncio.wait([func1(url_batch_of_3) func2 func3 for url_batch_of_3 in url_list])

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Pagination:

    def __init__(self, name: str, starting_url: str, page_selector: str, batch_size: int = 8,
                 proxy: bool = False, page_step: int = None, last_page: str = None,
                 url_queries: dict = None, pagination_query: str = None, render: bool = False):
        self.name = name
        self.starting_url = starting_url
        # Understand how the fuck this self.url_queries works and why it took half my lifetime to write it
        self.url_queries = (''.join(chain.from_iterable(e))
                            for e in product(*map(concat_keys_values, url_queries.items())))
        self.batch_size = batch_size
        self.page_selector = page_selector
        self.urls = (''.join(url) for url in product(list(starting_url.split()), self.url_queries))
        self.pagination_query = pagination_query
        self.page_number_selector = last_page
        self.page_step = page_step
        self.proxy = proxy
        self.render = render
        self.counter = 0
        self.asession = AsyncHTMLSession()
        self.asession.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                               '(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
        self.pages = []
        # TODO: product(self.urls, pagination_query, range(len(url_pages) + 1))
        # TODO: Convert arguments to **kwargs

    async def paginate(self, url):

        # TODO: Fix asyncio.sleep
        # TODO: Change proxy every batch not every iteration
        if self.proxy:
            while True:
                try:
                    r = await self.asession.get(url, verify=False)
                    if r.html.xpath('//span[contains(., "No Results for")]', first=True):
                        return
                    if self.render:
                        await r.html.arender(timeout=70)
                    else:
                        sleep(randint(1, 2))
                    break
                except ProxyError:
                    pass
        else:
            r = await self.asession.get(url)
            if r.html.xpath('//span[contains(., "No Results for")]', first=True):
                return
            if self.render:
                await r.html.arender(timeout=70)
            else:
                sleep(randint(1, 2))
        if not self.page_number_selector:
            urls = r.html.xpath(self.page_selector)
            try:
                urls = [''.join(x) for x in product(list(self.starting_url.split()), urls)]
                del urls[-1]
                urls.insert(0, r.url)
                [self.pages.append(link) for link in urls]
            except IndexError:
                self.pages.append(r.url)
        else:
            r = await self.asession.get(url)
            if r.html.xpath('//span[contains(., "No Results for")]', first=True):
                return
            if self.render:
                await r.html.arender(timeout=70)
            else:
                sleep(randint(1, 2))
            last_page = int(re.findall(r'\d+ of \d+', r.html.html)[0][-1])
            url_format = re.sub(repr(self.pagination_query).replace("'", '') + r'\d+',
                                r'', r.url, count=1)
            [self.pages.append(f'{url_format}{self.pagination_query}{str(n)}')
             for n in range(0, last_page * self.page_step, self.page_step)]

    async def paginator(self):
        url_list = list(self.urls)
        counter = 0
        proxy = get_nord()
        for urls in split_urls(url_list, self.batch_size):
            start = perf_counter()
            if self.proxy:
                while True:
                    try:
                        print(proxy)
                        self.asession.proxies = {'http': proxy, 'https': proxy}
                        await asyncio.wait([self.paginate(url) for url in urls])
                        break
                    except ProxyError:
                        print(f'Error connecting to http://{proxy}.nordvpn.com')
                        proxy = get_nord()
                        print(proxy)
                        await asyncio.wait([self.paginate(url) for url in urls])
            else:
                await asyncio.wait([self.paginate(url) for url in urls])
            self.counter += 1
            counter += len(urls)
            finish = perf_counter() - start
            if self.proxy:
                print(f'Finished First Paginator {len(urls)} in {finish:0.3f}. URLS: {len(self.pages)} total. - '
                      f'{(finish / len(urls)):0.3f} secs per request with {proxy.split("@")[1].split(".")[0]}')
            else:
                print(f'Finished First Paginator {len(urls)} in {finish:0.3f}. URLS: {len(self.pages)} total. - '
                      f'{(finish / len(urls)):0.3f} seconds per request')
        print("FINISHED "
              "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONE".split()*100)

    async def first_paginator(self):
        url_list = np.array_split(list(self.urls), 10)[0]
        counter = 0
        proxy = get_nord()
        for urls in split_urls(url_list, self.batch_size):
            start = perf_counter()
            if self.proxy:
                while True:
                    try:
                        print(proxy)
                        self.asession.proxies = {'http': proxy, 'https': proxy}
                        await asyncio.wait([self.paginate(url) for url in urls])
                        break
                    except ProxyError:
                        print(f'Error connecting to http://{proxy}.nordvpn.com')
                        proxy = get_nord()
                        print(proxy)
                        await asyncio.wait([self.paginate(url) for url in urls])
            else:
                await asyncio.wait([self.paginate(url) for url in urls])
            self.counter += 1
            counter += len(urls)
            finish = perf_counter() - start
            if self.proxy:
                print(f'Finished First Paginator {len(urls)} in {finish:0.3f}. URLS: {len(self.pages)} total. - '
                      f'{(finish / len(urls)):0.3f} secs per request with {proxy.split("@")[1].split(".")[0]}')
            else:
                print(f'Finished Third Paginator {len(urls)} in {finish:0.3f}. URLS: {len(self.pages)} total. - '
                      f'{(finish / len(urls)):0.3f} seconds per request')
        print("FINISHED "
              "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONE".split()*100)

    async def second_paginator(self):
        url_list = np.array_split(list(self.urls), 10)[1]
        counter = 0
        proxy = get_nord()
        for urls in split_urls(url_list, self.batch_size):
            start = perf_counter()
            if self.proxy:
                while True:
                    try:
                        print(proxy)
                        self.asession.proxies = {'http': proxy, 'https': proxy}
                        await asyncio.wait([self.paginate(url) for url in urls])
                        break
                    except ProxyError:
                        print(f'Error connecting to http://{proxy}.nordvpn.com')
                        proxy = get_nord()
                        print(proxy)
                        await asyncio.wait([self.paginate(url) for url in urls])
            else:
                await asyncio.wait([self.paginate(url) for url in urls])
            self.counter += 1
            counter += len(urls)
            finish = perf_counter() - start
            if self.proxy:
                print(f'Finished Second Paginator {len(urls)} in {finish:0.3f}. URLS: {len(self.pages)} total. - '
                      f'{(finish / len(urls)):0.3f} secs per request with {proxy.split("@")[1].split(".")[0]}')
            else:
                print(f'Finished Second Paginator {len(urls)} in {finish:0.3f}. URLS: {len(self.pages)} total. - '
                      f'{(finish / len(urls)):0.3f} seconds per request.')

    async def third_paginator(self):
        url_list = np.array_split(list(self.urls), 10)[2]
        counter = 0
        proxy = get_nord()
        for urls in split_urls(url_list, self.batch_size):
            start = perf_counter()
            if self.proxy:
                while True:
                    try:
                        print(proxy)
                        self.asession.proxies = {'http': proxy, 'https': proxy}
                        await asyncio.wait([self.paginate(url) for url in urls])
                        break
                    except ProxyError:
                        print(f'Error connecting to http://{proxy}.nordvpn.com')
                        proxy = get_nord()
                        print(proxy)
                        await asyncio.wait([self.paginate(url) for url in urls])
            else:
                await asyncio.wait([self.paginate(url) for url in urls])
            self.counter += 1
            counter += len(urls)
            finish = perf_counter() - start
            if self.proxy:
                print(f'Finished Second Paginator {len(urls)} in {finish:0.3f}. URLS: {len(self.pages)} total. - '
                      f'{(finish / len(urls)):0.3f} secs per request with {proxy.split("@")[1].split(".")[0]}')
            else:
                print(f'Finished Third Paginator {len(urls)} in {finish:0.3f}. URLS: {len(self.pages)} total. - '
                      f'{(finish / len(urls)):0.3f} seconds per request')
        print("FINISHED "
              "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONE".split()*100)

    async def fourth_paginator(self):
        url_list = np.array_split(list(self.urls), 10)[3]
        counter = 0
        proxy = get_nord()
        for urls in split_urls(url_list, self.batch_size):
            start = perf_counter()
            if self.proxy:
                while True:
                    try:
                        print(proxy)
                        self.asession.proxies = {'http': proxy, 'https': proxy}
                        await asyncio.wait([self.paginate(url) for url in urls])
                        break
                    except ProxyError:
                        print(f'Error connecting to http://{proxy}.nordvpn.com')
                        proxy = get_nord()
                        print(proxy)
                        await asyncio.wait([self.paginate(url) for url in urls])
            else:
                await asyncio.wait([self.paginate(url) for url in urls])
            self.counter += 1
            counter += len(urls)
            finish = perf_counter() - start
            if self.proxy:
                print(f'Finished Fourth Paginator {len(urls)} in {finish:0.3f}. URLS: {len(self.pages)} total. - '
                      f'{(finish / len(urls)):0.3f} secs per request with {proxy.split("@")[1].split(".")[0]}')
            else:
                print(f'Finished Fourth Paginator {len(urls)} in {finish:0.3f}. URLS: {len(self.pages)} total. - '
                      f'{(finish / len(urls)):0.3f} seconds per request')
        print("FINISHED "
              "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONE".split()*100)

    async def fifth_paginator(self):
        url_list = np.array_split(list(self.urls), 10)[4]
        counter = 0
        proxy = get_nord()
        for urls in split_urls(url_list, self.batch_size):
            start = perf_counter()
            if self.proxy:
                while True:
                    try:
                        print(proxy)
                        self.asession.proxies = {'http': proxy, 'https': proxy}
                        await asyncio.wait([self.paginate(url) for url in urls])
                        break
                    except ProxyError:
                        print(f'Error connecting to http://{proxy}.nordvpn.com')
                        proxy = get_nord()
                        print(proxy)
                        await asyncio.wait([self.paginate(url) for url in urls])
            else:
                await asyncio.wait([self.paginate(url) for url in urls])
            self.counter += 1
            counter += len(urls)
            finish = perf_counter() - start
            if self.proxy:
                print(f'Finished Fifth Paginator {len(urls)} in {finish:0.3f}. URLS: {len(self.pages)} total. - '
                      f'{(finish / len(urls)):0.3f} secs per request with {proxy.split("@")[1].split(".")[0]}')
            else:
                print(f'Finished Fifth Paginator {len(urls)} in {finish:0.3f}. URLS: {len(self.pages)} total. - '
                      f'{(finish / len(urls)):0.3f} seconds per request')
        print("FINISHED "
              "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONE".split()*100)

    async def sixth_paginator(self):
        url_list = np.array_split(list(self.urls), 10)[5]
        counter = 0
        proxy = get_nord()
        for urls in split_urls(url_list, self.batch_size):
            start = perf_counter()
            if self.proxy:
                while True:
                    try:
                        print(proxy)
                        self.asession.proxies = {'http': proxy, 'https': proxy}
                        await asyncio.wait([self.paginate(url) for url in urls])
                        break
                    except ProxyError:
                        print(f'Error connecting to http://{proxy}.nordvpn.com')
                        proxy = get_nord()
                        print(proxy)
                        await asyncio.wait([self.paginate(url) for url in urls])
            else:
                await asyncio.wait([self.paginate(url) for url in urls])
            self.counter += 1
            counter += len(urls)
            finish = perf_counter() - start
            if self.proxy:
                print(f'Finished Sixth Paginator {len(urls)} in {finish:0.3f}. URLS: {len(self.pages)} total. - '
                      f'{(finish / len(urls)):0.3f} secs per request with {proxy.split("@")[1].split(".")[0]}')
            else:
                print(f'Finished Sixth Paginator {len(urls)} in {finish:0.3f}. URLS: {len(self.pages)} total. - '
                      f'{(finish / len(urls)):0.3f} seconds per request')
        print("FINISHED "
              "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONE".split()*100)

    async def seventh_paginator(self):
        url_list = np.array_split(list(self.urls), 10)[6]
        counter = 0
        proxy = get_nord()
        for urls in split_urls(url_list, self.batch_size):
            start = perf_counter()
            if self.proxy:
                while True:
                    try:
                        print(proxy)
                        self.asession.proxies = {'http': proxy, 'https': proxy}
                        await asyncio.wait([self.paginate(url) for url in urls])
                        break
                    except ProxyError:
                        print(f'Error connecting to http://{proxy}.nordvpn.com')
                        proxy = get_nord()
                        print(proxy)
                        await asyncio.wait([self.paginate(url) for url in urls])
            else:
                await asyncio.wait([self.paginate(url) for url in urls])
            self.counter += 1
            counter += len(urls)
            finish = perf_counter() - start
            if self.proxy:
                print(f'Seventh Fifth Paginator {len(urls)} in {finish:0.3f}. URLS: {len(self.pages)} total. - '
                      f'{(finish / len(urls)):0.3f} secs per request with {proxy.split("@")[1].split(".")[0]}')
            else:
                print(f'Finished Seventh Paginator {len(urls)} in {finish:0.3f}. URLS: {len(self.pages)} total. - '
                      f'{(finish / len(urls)):0.3f} seconds per request')
        print("FINISHED "
              "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONE".split()*100)

    async def eighth_paginator(self):
        url_list = np.array_split(list(self.urls), 10)[7]
        counter = 0
        proxy = get_nord()
        for urls in split_urls(url_list, self.batch_size):
            start = perf_counter()
            if self.proxy:
                while True:
                    try:
                        print(proxy)
                        self.asession.proxies = {'http': proxy, 'https': proxy}
                        await asyncio.wait([self.paginate(url) for url in urls])
                        break
                    except ProxyError:
                        print(f'Error connecting to http://{proxy}.nordvpn.com')
                        proxy = get_nord()
                        print(proxy)
                        await asyncio.wait([self.paginate(url) for url in urls])
            else:
                await asyncio.wait([self.paginate(url) for url in urls])
            self.counter += 1
            counter += len(urls)
            finish = perf_counter() - start
            if self.proxy:
                print(f'Finished Eighth Paginator {len(urls)} in {finish:0.3f}. URLS: {len(self.pages)} total. - '
                      f'{(finish / len(urls)):0.3f} secs per request with {proxy.split("@")[1].split(".")[0]}')
            else:
                print(f'Finished Eighth Paginator {len(urls)} in {finish:0.3f}. URLS: {len(self.pages)} total. - '
                      f'{(finish / len(urls)):0.3f} seconds per request')
        print("FINISHED "
              "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONE".split()*100)

    async def ninth_paginator(self):
        url_list = np.array_split(list(self.urls), 10)[8]
        counter = 0
        proxy = get_nord()
        for urls in split_urls(url_list, self.batch_size):
            start = perf_counter()
            if self.proxy:
                while True:
                    try:
                        print(proxy)
                        self.asession.proxies = {'http': proxy, 'https': proxy}
                        await asyncio.wait([self.paginate(url) for url in urls])
                        break
                    except ProxyError:
                        print(f'Error connecting to http://{proxy}.nordvpn.com')
                        proxy = get_nord()
                        print(proxy)
                        await asyncio.wait([self.paginate(url) for url in urls])
            else:
                await asyncio.wait([self.paginate(url) for url in urls])
            self.counter += 1
            counter += len(urls)
            finish = perf_counter() - start
            if self.proxy:
                print(f'Finished Ninth Paginator {len(urls)} in {finish:0.3f}. URLS: {len(self.pages)} total. - '
                      f'{(finish / len(urls)):0.3f} secs per request with {proxy.split("@")[1].split(".")[0]}')
            else:
                print(f'Finished Ninth Paginator {len(urls)} in {finish:0.3f}. URLS: {len(self.pages)} total. - '
                      f'{(finish / len(urls)):0.3f} seconds per request')
        print("FINISHED "
              "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONE".split()*100)

    async def tenth_paginator(self):
        url_list = np.array_split(list(self.urls), 10)[9]
        counter = 0
        proxy = get_nord()
        for urls in split_urls(url_list, self.batch_size):
            start = perf_counter()
            if self.proxy:
                while True:
                    try:
                        print(proxy)
                        self.asession.proxies = {'http': proxy, 'https': proxy}
                        await asyncio.wait([self.paginate(url) for url in urls])
                        break
                    except ProxyError:
                        print(f'Error connecting to http://{proxy}.nordvpn.com')
                        proxy = get_nord()
                        print(proxy)
                        await asyncio.wait([self.paginate(url) for url in urls])
            else:
                await asyncio.wait([self.paginate(url) for url in urls])
            self.counter += 1
            counter += len(urls)
            finish = perf_counter() - start
            if self.proxy:
                print(f'Finished Tenth Paginator {len(urls)} in {finish:0.3f}. URLS: {len(self.pages)} total. - '
                      f'{(finish / len(urls)):0.3f} secs per request with {proxy.split("@")[1].split(".")[0]}')
            else:
                print(f'Finished Tenth Paginator {len(urls)} in {finish:0.3f}. URLS: {len(self.pages)} total. - '
                      f'{(finish / len(urls)):0.3f} seconds per request')
        print("FINISHED "
              "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONE".split()*100)

    def start(self, mode: str = 'multi'):
        if mode.lower() == 'single':
            start_time = perf_counter()
            self.asession.run(self.paginator)
            finish_time = perf_counter() - start_time
            print(f'Finished in {finish_time}', self.counter * 8, finish_time / (self.counter * 8))
        elif mode.lower() == 'multi':
            start_time = perf_counter()
            self.asession.run(*[self.first_paginator, self.second_paginator, self.third_paginator,
                              self.fourth_paginator, self.fifth_paginator, self.sixth_paginator,
                              self.seventh_paginator, self.eighth_paginator, self.ninth_paginator,
                              self.tenth_paginator])
            finish_time = perf_counter() - start_time
            print(f'Finished {self.counter} in {finish_time}. \n'
                  f'{self.counter * self.batch_size} requests '
                  f'with {finish_time / (self.counter * self.batch_size)} seconds per request')
        else:
            raise AttributeError
        return self

    def export(self, file_type):
        # TODO: Increment name to save old files
        df = pd.Series(self.pages, name='urls')
        if file_type.lower() == 'csv':
            df.to_csv(f'{self.name}_urls.csv', encoding='utf-8-sig')
        if file_type.lower() == 'pickle':
            df.to_pickle(f'{self.name}_urls.pkl')
        if file_type.lower() in ['excel', 'xlsx]']:
            df.to_excel(f'{self.name}_urls.xlsx', encoding='utf-8-sig')


if __name__ == "__main__":
    queries = {'/search?find_desc=': categories, '&find_loc=': locations}

    page = '//div/span/a[contains(@href, "&start=")][not(contains(@href, "?return_url="))]/@href'

    yelp_pages = Pagination(name='yelp', starting_url='https://www.yelp.com', proxy=True,
                            page_selector=page, url_queries=queries, batch_size=20)

    yelp_pages.start('multi').export('csv')
