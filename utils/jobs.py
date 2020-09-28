import os
from multiprocessing import Pool
from venom import Venom
import asyncio

splits = 6

lists = [str(i) for i in range(splits)]

processes = [f'jolse.py {splits} {i}' for i in lists]


def run_process(process):
    os.system(f'python {process}')


def filesplitter(file, splits):
    lists = [str(i) for i in range(splits)]
    processes = [f'{file}.py {splits} {i}' for i in lists]

    def run_process(process):
        os.system(f'python {process}')

    pool = Pool(processes=splits)
    pool.map(run_process, processes)


def start(inst):
    print(inst.chunk)


def jobs(*args, splits):
    pool = Pool(splits)
    arguments = [[*args] + [splits, i] for i in range(splits)]
    instances = [x for x in map(Venom, *zip(*arguments))]
    pool.map(start, instances)
    # start_url, cols, xpath, None, None, prod, regular_exp


if __name__ == '__main__':
    pool = Pool(processes=splits)
    pool.map(run_process, processes)
