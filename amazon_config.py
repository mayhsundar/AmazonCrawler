from selenium import webdriver

DIRECTORY = 'reports'
SEARCH_TERM = 'boat airpods 441'

BASE_URL = "http://www.amazon.in/"

def get_chrome_driver(options):
    return webdriver.Chrome("./chromedriver.exe", chrome_options=options)

def get_driver_options():
    return webdriver.ChromeOptions()

def set_ignore_certificate_error(options):
    options.add_argument('--ignore-certificate-errors')

def set_browser_as_incognito(options):
    options.add_argument('--incognito')    

 
