from playwright import async_playwright
import pandas as pd
from time import perf_counter
import asyncio
from multiprocessing import Process

s = perf_counter()


async def main():
    async with async_playwright() as p:
        urls = pd.read_csv('Jolse 2020-10-18.csv', index_col=0)['0'].to_list()[:10]
        browser_type = p.chromium
        browser = await browser_type.launch()
        page = await browser.newPage()
        for url in urls:
            await page.goto(url)
            sel = '//div[contains(@class, "normalpackage")]//p[@class="name"]/a'
            await page.waitForSelector(sel)
            elements = await page.querySelectorAll(sel)
            for el in elements:
                print(await el.innerText())
        await browser.close()


def run():
    asyncio.get_event_loop().run_until_complete(main())


if __name__ == '__main__':

    jobs = []
    for _ in range(5):
        jobs.append(Process(target=run))
    for job in jobs:
        job.start()
    for job in jobs:
        job.join()
    print(perf_counter() - s)
