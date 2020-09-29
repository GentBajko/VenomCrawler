from time import perf_counter

import pandas as pd
import numpy as np
import os


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


def check_files(chunksize: int, directory: str, filter_word):
    files = [file for file in os.listdir(directory) if filter_word in file]
    return chunksize == len(files)


def join_files(directory, filter_word):
    pages = pd.DataFrame()
    files = [file for file in os.listdir(directory) if filter_word in file]
    for file in files:
        df = pd.read_csv(f'{directory}/{file}', index_col=0)
        pages = pd.concat([pages, df], axis=0, join='outer')
        os.remove(file)
    pages = pages.reset_index().drop('index', axis=1)
    print(pages)
    return pages


if __name__ == "__main__":
    join_files(f'{os.getcwd()}/jolse.com', 'data')
