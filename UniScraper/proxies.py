from itertools import cycle

import requests
from lxml.html import fromstring


def get_proxy_pool():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxy_pool = set()
    for i in parser.xpath('//tbody/tr')[:20]:
        proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
        proxy_pool.add(proxy)
    return proxy_pool


proxies = get_proxy_pool()
proxy_pool = cycle(proxies)

nordn = [f"amichaluk%40hotmail.com:Adodasm33@{proxy}.nordvpn.com" for proxy in
           ['it146',
            'it147', 'it148', 'it149', 'it150', 'it151', 'it152', 'it153',
            'it154', 'it155', 'it156', 'it157', 'it158', 'it159', 'it160',
            'it161', 'it162', 'it163', 'it165', 'it166', 'it167', 'it168',
            'it169', 'it170', 'it171', 'it172', 'it173', 'it174', 'it175',
            'it176', 'it177', 'it178', 'it179', 'it180', 'it181', 'it182',
            'it183', 'it184', 'it185', 'it186', 'it187', 'it188', 'it189',
            'it190', 'it191', 'it192', 'it193', 'it194', 'it195', 'it196',
            'it197', 'it198', 'it199', 'it200', 'it201', 'it202', 'it203',
            'it204', 'it205', 'it206', 'it207', 'uk1783', 'uk1802', 'uk1803',
            'uk1813', 'uk1824', 'uk1826', 'uk1827', 'uk1831', 'uk1836',
            'uk1838', 'uk1842', 'uk1846', 'uk1847', 'uk1860', 'uk1866',
            'uk1900', 'uk1906', 'uk1919', 'uk1925', 'uk1927', 'uk1928',
            'uk1946', 'uk1960', 'uk1964', 'uk1988', 'uk1989', 'uk1996',
            'uk2001', 'uk2002', 'uk2005', 'uk2008', 'uk2009', 'uk2010',
            'uk2025', 'uk2029', 'uk2037', 'uk2040', 'uk2048', 'uk2060',
            'uk2065', 'uk2067', 'uk2081', 'uk2082', 'uk2086', 'uk2098',
            'uk2108', 'uk2111', 'uk2118', 'uk2150', 'uk2153', 'uk2155',
            'uk2158', 'us5082', 'us5396', 'us5398', 'us5407', 'us5410',
            'us5867', 'us6385']]

nordvpn = [f"amichaluk%40hotmail.com:Adodasm33@{proxy}.nordvpn.com" for proxy in
           ['it146',
            'it147', 'it148', 'it149', 'it150', 'it151', 'it152', 'it153',
            'it154', 'it155', 'it156', 'it157', 'it158', 'it159', 'it160','uk1803',
            'uk1813', 'uk1824', 'uk1826', 'uk1827', 'us5867', 'us6385']]

proxy = cycle(nordvpn)


def get_nord():
    return next(proxy)


def test():
    while True:
        try:
            proxy = next(proxy_pool)
            url = 'http://www.reddit.com'
            r = requests.get(url, proxies={"http": proxy, "https": proxy})
            print(f'{proxy} worked')
            break
        except Exception as e:
            print(f'{proxy} failed to connect because of {e}')


if __name__ == "__main__":
    test()
