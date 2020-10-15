import re
from fake_useragent import UserAgent
from fake_useragent import FakeUserAgentError


def find_elements(driver, xpath, _from: int = 0, to: int = None):
    return driver.find_elements_by_xpath(xpath)[_from:to]


def find_elements_by_text(driver, text: str, _from: int = 0, to: int = None):
    return driver.find_elements_by_xpath(f"//*[contains(text(), {text})]")[_from:to]


def find_regex(pattern, element):
    element = re.findall(pattern, element)[0]
    return "".join(element).strip()


def get_useragent(options):
    try:
        ua = UserAgent(cache=False, use_cache_server=False)
        options.add_argument(f"user-agent={ua['google chrome']}")
    except FakeUserAgentError:
        pass


if __name__ == '__main__':
    pass
