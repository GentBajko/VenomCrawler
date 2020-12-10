import asyncio
from playwright import async_playwright
from time import perf_counter
import re


class VenomBuilder:

    def __init__(self, urls):
        self.urls = [url if 'http://www.' in url else f'http://www.{url}' for url in urls]
        self.url_pages = []
        self.products = []

    async def start_browser(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False)
        self.page = await self.browser.newPage()

    async def __url_generator(self):
        for url in self.urls:
            yield url

    async def pagination(self, next_page, products):
        await self.start_browser()
        async for url in self.__url_generator():
            await self.page.goto(url)
            domain = re.findall(r'http://.*\.[A-z]+', url)[0]
            while True:
                s = perf_counter()
                try:
                    self.url_pages.append(self.page.url)
                    product_urls = [f"{domain}{await url.getAttribute('href')}" for url in
                                    await self.page.querySelectorAll(products)]
                    [self.products.append(url) for url in product_urls]
                    print('Finding next')
                    next_button = await self.page.querySelector(next_page)
                    await next_button.innerText()
                    print(perf_counter() - s)
                except Exception as e:
                    print(e)
                    break
        await self.page.close()


if __name__ == '__main__':
    Venom = VenomBuilder(['http://www.jolse.com/category/skincare/1018/'])
    asyncio.get_event_loop().run_until_complete(
        Venom.pagination('//p//a[@href="?page="]',
                         '//div[contains(@class, "normalpackage")]//p[@class="name"]/a')
    )
