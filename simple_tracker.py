import time
from amazon_config import (
    get_web_driver_options,
    get_chrome_web_driver,
    set_ignore_certificate_error,
    set_browser_as_incognito,
    NAME,
    CURRENCY,
    FILTERS,
    BASE_URL,
    DIRECTORY
    )
from selenium.webdriver.common.keys import Keys 
from selenium.common.exceptions import NoSuchElementException
import json
from datetime import datetime

class GenerateReport:      ## Generating the reposrt in json format
    def __init__(self, file_name, filters, base_link, currency, data):
        self.data = data
        self.file_name = file_name
        self.filters = filters
        self.base_link = base_link
        self.currency = currency
        report = {
            'title': self.file_name,
            'date': self.get_now(),
            'best_item': self.get_best_item(),
            'currency': self.currency,
            'filters': self.filters,
            'base_link': self.base_link,
            'products': self.data
        }
        print("Creating report...")
        with open(f'C:\\Users\\DELL\\Desktop\\Amazon_price_tracker\\Apple iphone13.json', 'w') as f:
            json.dump(report, f)
        print("Done...")

    @staticmethod
    def get_now():
        now = datetime.now()
        return now.strftime("%d/%m/%Y %H:%M:%S")

    def get_best_item(self):
        try:
            return sorted(self.data, key=lambda k: k['price'])[0]
        except Exception as e:
            print(e)
            print("Problem with sorting items")
            return None


class AmazonAPI:
    def __init__(self, search_term, filter, base_url, currency):
        self.base_url = base_url
        self.search_term = search_term
        options = get_web_driver_options()  
        set_ignore_certificate_error(options)
        set_browser_as_incognito(options)
        self.driver = get_chrome_web_driver(options)
        self.currency = currency
        self.price_filter = f"&rh=n%3A976460031%2Cp_36%3A{filter['min']}00-{filter['max']}00"  ## To avoid tracking by amazon we will use the parameteres given by with all the filters min - max price.
        pass

    def run(self):
        print("Starting Script.....")
        print(f"Looking for {self.search_term} products....")
        links = self.get_products_links() ## GEtting the list of the links of our product fro different sellers.
        if not links:
            print("Stopped script.")
            return
        print(f"Got {len(links)} links to products...")
        products = self.get_products_info(links) ##To get info of each product by iterating through our links lists that e created in get_products_link()
        print(f"Got info about {len(products)} products...")
        time.sleep(4)
        self.driver.quit()
        return products


    def get_products_links(self):
        self.driver.get(self.base_url)  #This method opens the given url in the browser. get id the method of driver object.
        time.sleep(3)
        element = self.driver.find_element_by_id("twotabsearchtextbox")
        element.send_keys(self.search_term)
        element.send_keys(Keys.ENTER)
        self.driver.get(f'{self.driver.current_url}{self.price_filter}')
        time.sleep(3)
        ## below we have a get the HTML Block code of all our results from the website in result_list
        result_list = self.driver.find_elements_by_class_name('s-result-list')
        links = []
        try:
            ## We will get HTML Code of each product lets say card of each product. 
            results = result_list[0].find_elements_by_xpath(
                "//div/span/div/div/div[2]/div[2]/div/div[1]/div/div/div[1]/h2/a")
            links = [link.get_attribute('href') for link in results]  ##Here we extract link from the the results list.
            return links
        except Exception as e:
            print("Didn't get any products...")
            print(e)
            return links
            
    def get_products_info(self, links):
        asins = self.get_asins(links)  ## Cleaning links. ASIN stands for Amazon Standard Identification Number. 
        ## It’s a 10-charcter alphanumeric unique identifier that’s assigned by Amazon.com and its partners.
        ## It’s primarily used for product-identification within their product catalog.
        products = []
        for asin in asins:
            product = self.get_single_product_info(asin)
            if product:
                products.append(product)
        return products


    def get_asins(self, links):
        return [self.get_asin(link) for link in links]

    def get_single_product_info(self, asin):
        print(f"Product ID: {asin} - getting data...")
        product_short_url = self.shorten_url(asin)
        self.driver.get(f'{product_short_url}?language=en_GB')
        time.sleep(2)
        title = self.get_title()
        seller = self.get_seller()
        price = self.get_price()
        if title and seller and price:
            product_info = {
                'asin': asin,
                'url': product_short_url,
                'title': title,
                'seller': seller,
                'price': price
            }
            return product_info
        return None

    def get_title(self):
        try:
            return self.driver.find_element_by_id('productTitle').text
        except Exception as e:
            print(e)
            print(f"Can't get title of a product - {self.driver.current_url}")
            return None

    def get_seller(self):
        try:
            return self.driver.find_element_by_id('bylineInfo').text
        except Exception as e:
            print(e)
            print(f"Can't get seller of a product - {self.driver.current_url}")
            return None

    def get_price(self):
        price = None
        try:
            price = self.driver.find_element_by_id('priceblock_ourprice').text
            price = self.convert_price(price)
        except NoSuchElementException:
            try:
                availability = self.driver.find_element_by_id('availability').text
                if 'Available' in availability:
                    price = self.driver.find_element_by_class_name('olp-padding-right').text
                    price = price[price.find(self.currency):]
                    price = self.convert_price(price)
            except Exception as e:
                print(e)
                print(f"Can't get price of a product - {self.driver.current_url}")
                return None
        except Exception as e:
            print(e)
            print(f"Can't get price of a product - {self.driver.current_url}")
            return None
        return price

    @staticmethod
    def get_asin(product_link):
        return product_link[product_link.find('/dp/') + 4:product_link.find('/ref')]

    def shorten_url(self, asin):
        return self.base_url + 'dp/' + asin

    def convert_price(self, price):
        price = price.replace(",", "")
        return float(price[2:])


if __name__ == '__main__':
    print("Hello")
    amazon = AmazonAPI(NAME, FILTERS, BASE_URL, CURRENCY)
    data = amazon.run()
    GenerateReport(NAME, FILTERS, BASE_URL, CURRENCY, data)