import threading
from selenium.common.exceptions import NoSuchElementException,\
    UnexpectedAlertPresentException
from .composer import Composer


class Paginate(Composer):
    def __init__(self, name: str, starting_url: str,
                 column_names: list, xpaths: list,
                 next_xpath: str = None, product_xpath: str = None,
                 chunksize: int = None, chunk: int = None):
        super().__init__(name, starting_url, column_names, xpaths,
                         next_xpath, product_xpath, chunksize, chunk)

    def pagination(self):
        self.urls = iter(self.urls)
        while True:
            try:
                url = next(self.urls)
                self.driver.get(url)
                if not self.error():
                    while True:
                        self.source.append(self.driver.current_url)
                        if self.product_xpath:
                            self.get_services(self.driver.current_url)
                        try:
                            self.driver.find_element_by_xpath(
                                self.next_xpath
                            ).click()
                        except (NoSuchElementException,
                                UnexpectedAlertPresentException):
                            break
            except StopIteration:
                break
        self.save(self.source, 'pages')
        self.save(self.products, 'products')
        return self

    def __run(self):
        self.pagination().scrape()


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
