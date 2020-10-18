from threading import Thread
from selenium.common.exceptions import NoSuchElementException, \
    UnexpectedAlertPresentException
from .composer import Composer


class Paginate(Composer):
    def __init__(self, name: str, starting_url: str,
                 column_names: list, xpaths: list,
                 next_xpath: str = None, product_xpath: str = None,
                 chunksize: int = None, chunk: int = None):
        super(Paginate, self).__init__(name=name, starting_url=starting_url,
                                       column_names=column_names,
                                       xpaths=xpaths, next_xpath=next_xpath,
                                       product_xpath=product_xpath,
                                       chunksize=chunksize, chunk=chunk)

    def pagination(self):
        self.urls = iter(self.urls)
        counter = 1
        while True:
            try:
                url = next(self.urls)
                self.driver.get(url)
                if not self.error():
                    counter += 1
                    while True:
                        self.source.append(self.driver.current_url)
                        if self.product_xpath:
                            self.get_services(self.driver.current_url)
                        try:
                            self.driver.find_element_by_xpath(self.next_xpath).click()
                        except (NoSuchElementException,
                                UnexpectedAlertPresentException):
                            break
            except StopIteration:
                break
        self.save(self.source, 'pages')
        self.save(self.products, 'products')
        self.products = self.products * 76
        return self

    def run(self):
        self.pagination().scrape()

    def run_threads(self):
        jobs = []
        for i in range(self.chunksize):
            self.chunksize = i
            thread = Thread(target=self.pagination)
            jobs.append(thread)
        for job in jobs:
            job.start()
        for job in jobs:
            job.join()
        jobs = []
        for _ in range(self.chunksize):
            thread = Thread(target=self.scrape)
            jobs.append(thread)
        for job in jobs:
            job.start()
        for job in jobs:
            job.join()

        self.driver.close()


class Search(Composer):
    def __init__(self, name: str, starting_url: str,
                 column_names: list, xpaths: list,
                 next_xpath: str = None, product_xpath: str = None,
                 chunksize: int = None, chunk: int = None):
        super().__init__(name, starting_url, column_names, xpaths,
                         next_xpath, product_xpath, chunksize, chunk)

    def search(self):
        urls = self.urls
        self.search_terms = self.check_split(self.search_terms)
        while True:
            try:
                url = next(urls)
                self.driver.get(url)
                search = self.driver.find_element_by_xpath(
                    self.search_xpath
                )
                while True:
                    try:
                        search_term = next(self.search_terms)
                        search.send_keys(search_term)
                        if not self.error():
                            url = self.driver.current_url
                            self.source.append(url)
                    except StopIteration:
                        break
            except StopIteration:
                break
        return self

    def run(self):
        self.search().scrape()


if __name__ == '__main__':
    pass
