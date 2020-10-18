from Venom.utils.jobs import Venom
import os
import pandas as pd
from Venom.Venom import Paginate
from threading import Thread

if __name__ == '__main__':
    starting_url = 'https://glowyskinshop.com/shop'
    column_names = ['Product', 'Price', 'Discounted Price', 'Description']
    xpaths = [
        '//h1[@class="product_title entry-title"]',
        '//p[@class="price"]//span[@class="woocommerce-Price-amount amount"]/bdi',
        '//p[@class="price"]/span/ins/span/bdi',
        '//div[@class="woocommerce-product-details__short-description"]/p'
    ]
    product_xpath = '//div[@class="astra-shop-summary-wrap"]/a'
    page_query = "/page/"
    page_steps = 1
    last_page_xpath = '//div/nav/ul/li[a][last()-1]/a'
    next_xpath = '//li/a[@class="next page-numbers"]'
    regex = {'Price': "(\d+,)?(\d+)", 'Discounted Price': "(\d+,)?(\d+)"}

    # glowy = Paginate("Glowyskin", starting_url=starting_url, column_names=column_names,
    #                  xpaths=xpaths, product_xpath=product_xpath)
    # glowy.run()

    jobs = []
    for i in range(6):
        glowy = Paginate("Glowyskin", starting_url=starting_url, column_names=column_names, next_xpath=next_xpath,
                         xpaths=xpaths, product_xpath=product_xpath, chunksize=6, chunk=i)
        thread = Thread(target=glowy.run)
        jobs.append(thread)
    for job in jobs:
        job.start()
    for job in jobs:
        job.join()

    from datetime import datetime

    print(datetime.now())
    # Venom("Glowyskin", starting_url=starting_url, column_names=column_names,
    #       xpaths=xpaths, product_xpath=product_xpath, chunksize=6)
    # files = [pd.read_csv(f'data/Glowyskin/data/{file}', index_col=0, encoding='utf-8-sig')
    #          for file in os.listdir('data/Glowyskin/data')
    #          if 'Glowyskin' in file and file.endswith('.csv') and file != 'Glowyskin.csv']
    # df = pd.concat(files).reset_index().drop('index', axis=1)
    # df['Price'] = df['Price'].apply(lambda x: float(str(x).replace(',', '')))
    # df['Discounted Price'] = df['Discounted Price'].apply(lambda x: float(str(x).replace(',', '')))
    # df['Discount %'] = (df['Discounted Price'].divide(df['Price'])).apply(lambda x: (1 - x) * 100)
    # df['Discount %'] = df['Discount %'].round(2)
    # df.index += 1
    # df.to_csv('data/Glowyskin/data/Glowyskin.csv', encoding='utf-8-sig')
