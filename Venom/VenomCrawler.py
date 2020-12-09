import asyncio
from playwright import async_playwright
from time import sleep


class VenomCrawler:

    def __init__(self):
        await self.__start_browser()

    async def __start_browser(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False)

    async def start_page(self, url):
        # Put this code on another async
        page = await self.browser.newPage()
        await page.goto(url)
        # code
        print(page.url)
        # code
        await page.close()


if __name__ == '__main__':
    Venom = VenomCrawler()
    asyncio.get_event_loop().run_until_complete(Venom.start_page('http://www.jolse.com'))
