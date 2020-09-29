from venom import Venom


class Jolse(Venom):
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


if __name__ == '__main__':
    jolse = Jolse("Jolse")
    jolse.init_driver().calculate_urls().get_services_urls().scrape()
