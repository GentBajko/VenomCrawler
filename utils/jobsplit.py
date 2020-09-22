import pickle
from multiprocessing import Pool


class Test:

    def __init__(self, num, test):
        self.num = num
        self.test = test

    def get(self):
        return self.num + self.test


def placeholder(*args):
    Test(args).get()


# pool = Pool(processes=10)
# pool.map(placeholder, [x for x in range(10)])

a = {'num': "O", 'test': 'Hi'}

# placeholder(*a.values())
eval(Test(*a.values()).get())
