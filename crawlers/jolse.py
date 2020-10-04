from utils.jobs import Venom

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
    Venom(name="Glowyskin", starting_url=starting_url, column_names=column_names,
          xpaths=xpaths, product_xpath=product_xpath, page_query=page_query,
          page_steps=page_steps, last_page_xpath=last_page_xpath, regex=regex)
