from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import asyncio
import time

import aiohttp

from aioselenium import Remote, Keys
from requests_html import HTML, AsyncHTMLSession


async def scraper(url):
    async with aiohttp.ClientSession() as session:
        capabilities = DesiredCapabilities.CHROME

        command_executor = 'http://localhost:4444/wd/hub'

        remote = await Remote.create(command_executor, capabilities, session)
        async with remote as driver:
            await driver.set_window_size(1920, 1080)
            await driver.get(url)
            # print('Loaded:', await driver.source())
            source = await driver.source()
            s = HTML(html=source)
            products = s.xpath('//div[@class="astra-shop-summary-wrap"]/a/@href')
            for product in products:
                await driver.get(product)
                src = await driver.source()
                s = HTML(html=src)
                print(s.xpath('//h1[@class="product_title entry-title"]/text()', first=True))


async def main(urls):
    await asyncio.gather(*[scraper(url) for url in urls])


if __name__ == "__main__":
    s = time.perf_counter()

    urls = [
        'https://glowyskinshop.com/shop/?v=79cba1185463',
        'https://glowyskinshop.com/shop/page/2/?v=79cba1185463',
        'https://glowyskinshop.com/shop/page/3/?v=79cba1185463',
        'https://glowyskinshop.com/shop/page/4/?v=79cba1185463',
        'https://glowyskinshop.com/shop/page/5/?v=79cba1185463',
    ]

    products = asyncio.run(main(urls))

    elapsed = time.perf_counter() - s
    print(f"Executed in {elapsed:0.2f} seconds.")
