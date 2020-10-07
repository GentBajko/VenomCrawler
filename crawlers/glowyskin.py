from utils.jobs import Venom

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

    Venom("Glowyskin", starting_url=starting_url, column_names=column_names,
          xpaths=xpaths, product_xpath=product_xpath, page_query=page_query,
          page_steps=page_steps, last_page_xpath=last_page_xpath, regex=regex, chunksize=6)
