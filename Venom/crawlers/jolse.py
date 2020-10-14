from Venom.utils.jobs import Venom
import os
import pandas as pd

if __name__ == '__main__':
    starting_url = 'https://jolse.com/category/skincare/1018'
    column_names = ['Brand', 'Product', 'Price', 'Discounted Price']
    xpaths = ['//tr[@class="prd_brand_css  xans-record-"]//td/span[contains(@style,"color")]',
              '//div[@class="headingArea "]/h2',
              '//td/span/strong[@id="span_product_price_text"]',
              '//span/span[@id="span_product_price_sale"]']
    product_xpath = '//div[contains(@class, "normalpackage")]//p[@class="name"]/a'
    regex = {'Price': '\d+\.\d+', 'Discounted Price': '\d+\.\d+'}
    last_page_xpath = '//li[@class="xans-record-"]/a[@class="this"]'
    last_page_arrow = '//p[@class="last"]'
    page_query = '?page='
    page_steps = 1
    Venom(name="Jolse Time Deals", starting_url='https://jolse.com/category/time-deal/1097/', column_names=column_names,
          xpaths=xpaths, product_xpath='//p[@class="name"]/a', regex=regex, chunksize=10)
    Venom(name="Jolse", starting_url=starting_url, column_names=column_names,
          xpaths=xpaths, product_xpath=product_xpath, page_query=page_query,
          page_steps=page_steps, last_page_xpath=last_page_xpath,
          last_page_arrow=last_page_arrow, regex=regex, chunksize=8)
    files = [pd.read_csv(f'data/Jolse/data/{file}', index_col=0, encoding='utf-8-sig')
             for file in os.listdir('data/Jolse/data')
             if 'Jolse' in file and file.endswith('.csv') and file != 'Jolse.csv']
    df = pd.concat(files).reset_index().drop('index', axis=1)
    df['Discount %'] = (df['Discounted Price'].divide(df['Price'])).apply(lambda x: (1 - x) * 100)
    df['Discount %'] = df['Discount %'].round(2)
    df.index += 1
    df.to_csv('data/Jolse/data/Jolse.csv', encoding='utf-8-sig')
