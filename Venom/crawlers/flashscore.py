import undetected_chromedriver as uc

uc.install()
from selenium.webdriver import Chrome, ChromeOptions
from selenium.common.exceptions import NoSuchElementException
from Venom.Venom import Venom
from time import sleep
import pandas as pd

urls = pd.read_csv('/home/gent/Documents/Projects/VenomCrawler/Venom/crawlers/archives.csv')['0'].to_list()
login_button = '//div[@id="signIn"]'
user = '//input[@id="email"]'
password = '//div[@class="password-form-element border-bottom"]/input'
submit = '//div[@class="sign-up-form-element"]/input'


def get_league_links():
    driver = Chrome()
    driver.get("https://www.flashscore.com/")
    driver.find_element_by_xpath(login_button).click()
    sleep(2)
    driver.find_element_by_xpath(user).send_keys('gent.bajko@gmail.com')
    sleep(2)
    driver.find_element_by_xpath(password).send_keys('Shinsekainokam1')
    sleep(2)
    driver.find_element_by_xpath(submit).click()
    # login('//div[@id="signIn"]', 'gent.bajko@gmail.com', 'Shinsekainokam1', '//input[@id="email"]',
    #       'div[@class="password-form-element border-bottom"]/imput', '//input[@id="submit"]')
    sleep(5)
    championships = driver.find_elements_by_xpath('//ul[@id="my-leagues-list"]/li/a')
    country = [x.get_attribute('title').split(': ')[0].capitalize() for x in championships]
    champ = [x.text for x in championships]
    urls = [x.get_attribute('href') + 'archive/' for x in championships]

    def find_elements(xpath, _from: int = 0, to: int = None):
        return driver.find_elements_by_xpath(xpath)[_from:to]

    res = []
    for url in urls:
        driver.get(url)
        a = find_elements('//div[@id="tournament-page-archiv"]//div[@class="leagueTable__season"]//a', 0, 2)
        for x in a:
            res.append(x.get_attribute('href'))
        print(res)
    res = [x + 'results/' for x in res]
    pd.Series(res).to_csv('archives.csv')


# get_league_links()

year = '//div[@class="teamHeader__text"]'
date = '//div[@class="event__time"]'
time = '//div[@class="event__time"]'
home_team = '//div[contains(@class,"event__participant event__participant--home")]'
away_team = '//div[contains(@class,"event__participant event__participant--away")]'
homeTeamFt = '//img[@class="event__logo event__logo--home"]/following-sibling::div/span[1]'
awayTeamFt = '//img[@class="event__logo event__logo--home"]/following-sibling::div/span[2]'
homeTeamHt = '//div[@class="event__part"]'
awayTeamHt = '//div[@class="event__part"]'
load_more = '//a[@class="event__more event__more--static"]'
regex = {'homeTeamHt': '\d', 'awayTeamHt': ' \d', 'date': '\d+\.\d+', 'time': '\d+:\d+'}
cols = ['date', 'time', 'homeTeam', 'awayTeam', 'homeTeamFt', 'awayTeamFt', 'homeTeamHt', 'awayTeamHt']
xpaths = [date, time, home_team, away_team, homeTeamFt, awayTeamFt, homeTeamHt, awayTeamHt]

flashscore = Venom('flashscore', 'https://www.flashscore.com', cols, xpaths,
                   predefined_url_list=urls, load_more=load_more, regex=regex,
                   chunksize=6)
flashscore.run_threads()
