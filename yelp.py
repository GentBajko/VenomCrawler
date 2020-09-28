from time import perf_counter
from venom import Venom
import pandas as pd
import dill

if __name__ == '__main__':
    start_time = perf_counter()

    csv = pd.read_csv('CityList.csv', encoding='utf-8-sig')
    locations = (f'{city.replace(" ", "%20")}%2C%20{country}' for city, country in
                 zip(csv['City'], csv['Country']))
    categories = ['Adult Entertainment',
                  'Beauty & Spas',
                  'Jewelry',
                  'Computer/Software and Media Streaming',
                  'Electronics Stores',
                  'Betting and Casino Gambling']
    columns = ['Title', 'Merchant Name', 'Merchant Category', 'Address', 'Street Name', 'City', 'State', 'Country',
               'Zipcode', 'Phone no', 'Pricing level', 'Star rating', 'Amenities', 'Hours of Operations']
    selectors = ['//title', '//div/h1', '//div/span/span/a', '//address', '//address/p', '//address/p[last() - 1]',
                 '//address/p[last()]', '//address/p[last()]', '//address/p[last() - 1]',
                 '//section//div[span]/following-sibling::div/p[contains(.,"+")]',
                 '//span/span[contains(.,"€") or contains(.,"£")]',
                 '//div[contains(@aria-label, "star rating")]/@aria-label',
                 '//div[div[h4[contains(.,"Amenities")]]]/following-sibling::div', '//table[contains(.,"Mon")]']
    start_url = 'http://www.yelp.com/search?'
    queries = {'find_desc=': categories, '&find_loc=': locations}
    errors = ["//h3[contains(.,'the page of results you requested is unavailable.')]", '//span[@class="page-status"]',
              "//span[contains(.,'No Results for')]", '//p[contains(.,"Suggestions for improving the results:")]']
    business_xpath = '//div[h4]//span/a'
    regular_exp = {'Zipcode': r'( \w{3})( )(\w{3})|(^\d+)', 'City': r'[A-z]{2,20}.[A-z]{2,20}'}

    for i in range(4):
        with open('test', 'wb') as f:
            dill.dump(Venom(starting_url=start_url, column_names=columns, xpaths=selectors, url_queries=queries,
                            error_xpaths=errors, product_xpath=business_xpath, regex=regular_exp, chunksize=4, chunk=i),
                      f)

    # predefined_urls = pd.read_csv('yelp data.csv')['url'].tolist()
    # yelp.calculate_urls('&start=', 30, '//div/span[contains(.," of ")]')

    finish = perf_counter() - start_time
    hours = (finish // 60) // 60
    minutes = (finish // 60) % 60
    seconds = finish % 60

    print(f'\nFinished in {hours} hour(s), {minutes} minute(s) and {seconds} seconds.')
