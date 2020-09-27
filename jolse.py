from venom import Venom

cols = ['Product', 'Real Price', 'Discounted Price']
xpath = ['//div[contains(@class, "normalpackage")]//p[@class="name"]/a',
         '//div[contains(@class, "normalpackage")]//li[@item-title="Price"]/span',
         '//div[contains(@class, "normalpackage")]//li[@item-title="Price"]/following-sibling::li/span']
start_url = 'https://jolse.com/category/skincare/1018'
last_page = '//p[@class="last"]'
page = 'page='
steps = 1
last_page_xpath = '//li[@class="xans-record-"]/a[@class="this"]'
regular_exp = {'Real Price': r'\d+\.\d+', 'Discounted Price': r'\d+\.\d+'}

jolse = Venom(starting_url=start_url, column_names=cols, xpaths=xpath, regex=regular_exp, splits=10)

jolse.calculate_urls(page_query=page, page_steps=steps, last_page_xpath=last_page_xpath,
                     last_page_arrow=last_page).get_services_urls().scrape()
