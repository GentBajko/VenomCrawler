from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import asyncio
import time

import aiohttp

from aioselenium import Remote
from requests_html import HTML
import pandas as pd
from collections.abc import AsyncIterable, AsyncGenerator

data = {'Brand': [], 'Product': [], 'Price': [], 'Discounted Price': []}
async def scraper(url):
    async with aiohttp.ClientSession() as session:
        capabilities = DesiredCapabilities.FIREFOX

        command_executor = 'http://localhost:4444/wd/hub'

        remote = await Remote.create(command_executor, capabilities, session)
        async with remote as driver:
            await driver.set_window_size(1920, 1080)
            await driver.get(url)
            source = await driver.source()
            s = HTML(html=source)
            products = s.xpath('//div[contains(@class, "normalpackage")]//p[@class="name"]/a/@href')
            xpaths = ['//tr[@class="prd_brand_css  xans-record-"]//td/span[contains(@style,"color")]',
                      '//div[@class="headingArea "]/h2',
                      '//td/span/strong[@id="span_product_price_text"]',
                      '//span/span[@id="span_product_price_sale"]']
            for product in products:
                await driver.get('https://jolse.com/' + product)
                src = await driver.source()
                s = HTML(html=src)
                data['Brand'].append(s.xpath(f'{xpaths[0]}/text()', first=True))
                print(s.xpath(f'{xpaths[3]}/text()', first=True))
                data['Product'].append(s.xpath(f'{xpaths[1]}/text()', first=True))
                data['Price'].append(s.xpath(f'{xpaths[2]}/text()', first=True))
                data['Discounted Price'].append(s.xpath(f'{xpaths[3]}/text()', first=True))


async def main(urls):
    await asyncio.gather(*[scraper(url) for url in urls])


if __name__ == "__main__":
    start = time.perf_counter()

    urls = pd.read_csv('Jolse 2020-10-18.csv', index_col=0)['0'].to_list()[:6]

    asyncio.run(main(urls))
    pd.DataFrame(data).to_csv('test.csv', encoding='utf-8-sig')

    elapsed = time.perf_counter() - start
    print(f"Executed in {elapsed:0.2f} seconds.")
