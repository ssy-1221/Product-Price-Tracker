from selenium import webdriver

DIRECTORY = 'reports'
NAME = 'Apple iphone13'
CURRENCY = '₹'
MIN_PRICE = '5000'
MAX_PRICE = '65000'
FILTERS = {
    'min': MIN_PRICE,
    'max': MAX_PRICE
}

BASE_URL = "http://www.amazon.in/"

#get our chrome webdriver that we installed
def get_chrome_web_driver(options):
    return webdriver.Chrome('./chromedriver', chrome_options=options)

##Provides functionality to us for chrome web browser  
# like visiting untrusted websites, opening in incognito mode etc.
def get_web_driver_options():
    return webdriver.ChromeOptions()

#to ignore the certificate errors i.e. visit untrusted websites.
def set_ignore_certificate_error(options):
    options.add_argument('--ignore-certificate-errors')

#to open browsers incognito
def set_browser_as_incognito(options):
    options.add_argument('--incognito')