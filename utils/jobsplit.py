class Test:

    def __init__(self, num):
        self.num = num

    def get(self):
        print(self.num)


from multiprocessing import Pool


def placeholder(num):
    Test(num).get()


pool = Pool(processes=10)
pool.map(placeholder, [x for x in range(10)])