from itertools import product, chain
from time import perf_counter

import numpy as np
import pandas as pd

selectors = {"Title": '//title', "Merchant Name": None, "Merchant Category": None, "Address": None, "Street Name": None,
             "City": None, "State": None, "Country": None, "Zipcode": '//address/p[last() - 1]',
             "Phone no": '//section//div[span]/following-sibling::div/p[contains(.,"+")]',
             "Pricing level": '//span/span[contains(.,"€") or contains(.,"£")]',
             "Star rating": '//div[contains(@aria-label, "star rating")]/@aria-label',
             "Amenities": '//div[div[h4[contains(.,"Amenities")]]]/following-sibling::div',
             "Hours of Operations": '//table[contains(.,"Mon")]'}

data = {key: [] for key in selectors}

csv = pd.read_csv('CityList.csv', encoding='utf-8-sig')

locations = (f'{city.replace(" ", "%20")}%2C%20{country}' for city, country in zip(csv['City'], csv['Country']))

categories = (cat.replace(" ", "%20").replace("/", '%2F') for cat in ['Adult Entertainment',
                                                                      'Beauty & Spas',
                                                                      'Jewelry',
                                                                      'Computer/Software and Media Streaming',
                                                                      'Electronics Stores',
                                                                      'Betting and Casino Gambling'])


def timer(func):
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        finish = perf_counter()
        print(result, f'{(finish - start):0.12f}')
        return result
    return wrapper


def get_selectors(columns: list, selectors: list):
    # TODO: If shorter selector col then np.NaN
    if len(columns) == len(selectors):
        return {k: v for k, v in zip(columns, selectors)}
    raise AttributeError


def concat_keys_values(tupl):
    k, values = tupl
    return (k + v for v in values)


def split_urls(urls_list, batch_size):
    for i in np.arange(0, len(list(urls_list)), batch_size):
        yield list(urls_list)[i:i + batch_size]


if __name__ == "__main__":
    print(list(locations))
