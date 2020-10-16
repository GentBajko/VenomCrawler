import re
import os
from fake_useragent import UserAgent
from fake_useragent import FakeUserAgentError
from .utils import join_files, check_files


def find_regex(pattern, element):
    element = re.findall(pattern, element)[0]
    return "".join(element).strip()


def get_useragent(options):
    try:
        ua = UserAgent(cache=False, use_cache_server=False)
        options.add_argument(f"user-agent={ua['google chrome']}")
    except FakeUserAgentError:
        pass


def save_data(crawler_name, df_name, data, filename,  chunksize, chunk, path, date):
    data.to_csv(f'{path}/{df_name} {chunk}.csv', encoding='utf-8-sig')
    if not check_files(path, df_name, chunksize):
        return
    full_data = join_files(path, df_name)
    if filename not in os.listdir(path):
        full_data.to_csv(f"{path}/{filename}", encoding='utf-8-sig')
    else:
        count = len([file for file in os.listdir(path) if filename in file])
        full_data.to_csv(f"{path}/{crawler_name} {date} {count}.csv", encoding='utf-8-sig')


if __name__ == '__main__':
    pass
