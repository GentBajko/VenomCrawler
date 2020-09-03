import os
from multiprocessing import Pool

splits = 16

lists = [str(i) for i in range(splits)]

processes = [f'Venom.py {splits} {i}' for i in lists]


def run_process(process):
    os.system(f'python {process}')


if __name__ == '__main__':
    pool = Pool(processes=splits)
    pool.map(run_process, processes)
