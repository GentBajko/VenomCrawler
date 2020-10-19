import os
from time import perf_counter

import numpy as np
import pandas as pd


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
    files = [file for file in os.listdir(directory)
             if filter_word in file and file.endswith('csv')]
    for file in files:
        file_path = os.path.join(directory, file)
        df = pd.read_csv(file_path, index_col=0)
        pages = pd.concat([pages, df], axis=0, join='outer')
        os.remove(file_path)
    pages = pages.reset_index().drop('index', axis=1)
    pages.index += 1
    return pages


def check_url_prefix(url):
    if "http://" not in url:
        return f"http://{url}"
    return url


def add_date(data, date):
    if type(data) == list:
        df = pd.Series(data)
    else:
        df = pd.DataFrame(data)
        columns = ['Date'] + df.columns.to_list()
        df['Date'] = [date] * len(df)
        df = df[columns]
    return df


def get_path(crawler_name, df_name):
    if 'crawlers' not in os.listdir(os.getcwd()):
        path = os.path.join(os.getcwd(), 'crawlers',
                            'data', crawler_name, df_name)
    else:
        path = os.path.join(os.getcwd(), 'data',
                            crawler_name, df_name)
    os.makedirs(path, exist_ok=True)
    return path


def add_row(path, cols: list = None, *args):
    line = ",".join([str(x) for x in args])
    if os.path.isfile(path):
        with open(path, 'a') as csv:
            csv.write(line)
    else:
        with open(path, 'w') as csv:
            csv.write(",".join([str(x) for x in cols]))
            csv.write(line)


if __name__ == "__main__":
    pass
