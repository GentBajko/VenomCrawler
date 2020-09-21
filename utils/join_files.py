import os
import pandas as pd

pages = pd.DataFrame(dtype=object)
for file in os.listdir('www.yelp.com'):
    print
    df = pd.read_csv(f'www.yelp.com/{file}', index_col=0)
    pages = pd.concat([pages, df])
pages.reset_index().drop('index', axis=1)
pages.to_csv('www.yelp.com.csv')
