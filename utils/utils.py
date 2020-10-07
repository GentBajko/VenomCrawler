import os
from time import perf_counter

import numpy as np
import pandas as pd
from shadow_useragent import ShadowUserAgent


def timer(func):
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        finish = perf_counter()
        print(result, f'{(finish - start):0.12f}')
        return result

    return wrapper


def get_selectors(columns: list, xpaths: list):
    if len(columns) == len(xpaths):
        return {k: v for k, v in zip(columns, xpaths)}
    raise AttributeError


def concat_keys_values(tupl):
    k, values = tupl
    return (k + v for v in values)


def split_urls(urls_list, batch_size):
    for i in np.arange(0, len(list(urls_list)), batch_size):
        yield list(urls_list)[i:i + batch_size]


def check_files(directory: str, filename, chunksize):
    files = [file for file in os.listdir(directory) if filename in file and file.endswith('csv')]
    return len(files) == chunksize


def join_files(directory, filter_word):
    pages = pd.DataFrame()
    files = [file for file in os.listdir(directory) if filter_word in file and file.endswith('csv')]
    for file in files:
        file_path = os.path.join(directory, file)
        df = pd.read_csv(file_path, index_col=0)
        pages = pd.concat([pages, df], axis=0, join='outer')
        os.remove(file_path)
    pages = pages.reset_index().drop('index', axis=1)
    return pages


if __name__ == "__main__":
    pass
