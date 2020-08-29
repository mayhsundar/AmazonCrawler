import amazon_config as config;
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
import json

class MakeReport:
    def __init__(self, fileName, products):
        self.fileName = fileName
        self.products = products

        report = {
            'title': self.fileName,
            'date': self.get_current_date(),
            'cheapestItem': self.get_cheapestItem(),
            'products':self.products
        }

        print("printing report")
        with open(f"{config.DIRECTORY}/{fileName}.json","w") as f:
            json.dump(report, f)
        print("printing report done :)")    

    def get_current_date(self):
        now = datetime.now()
        return now.strftime("%d/%m/%Y %H:%M:%S")

    def get_cheapestItem(self):
        try:
            return sorted(self.products, key=lambda keyTitle:keyTitle['cost'])[0]
        except Exception as e:
            print("Error while sorting products")
            print(e)
            return None

class AmazonAPI:

    def __init__(self):
        options = config.get_driver_options()
        config.set_ignore_certificate_error(options)
        config.set_browser_as_incognito(options)
        self.driver = config.get_chrome_driver(options)
        pass
        

    def run(self):
        print(f"Crawler has woken up and started working...")
        print(f"Searching for {config.SEARCH_TERM}...")
        self.prepareAmazonSite()
        links = []
        for page in range(1, self.pages+1):
            #print(self.mainUrl+"&page="+str(page))
            links = [*self.getProductsLinks(self.mainUrl+"&page="+str(page))]
        
        if not links:
            print(" Crawler got into a problem!!!, so stopped")
            return
        print(f"Got {len(links)} products for {config.SEARCH_TERM}")    
        print("Fetching product details...")
        products = self.getProductsDetails(links)

        return products
        
    def prepareAmazonSite(self):
        self.driver.maximize_window()
        self.mainUrl = self.getUrlWithSearchItem()
        self.driver.get(self.mainUrl)
        time.sleep(3)
        self.pages = self.getNoOfPages()

    def getUrlWithSearchItem(self):
        return config.BASE_URL+"s?k="+config.SEARCH_TERM

    def getNoOfPages(self):
        try:
            lastPage = self.driver.find_element_by_xpath("//li[@class='a-disabled'][2]")
            return int(lastPage.text.strip())
        except NoSuchElementException:
            try:
                lastPage = self.driver.find_elements_by_xpath("//ul[@class='a-pagination']/li")
                return int(len(lastPage))-2
            except NoSuchElementException:
                return 1    

    def getProductsDetails(self, links):
        productDetails = []
        for cLink in links:
            productDetails.append(self.getSingleProductInfo(cLink))
        return productDetails      
   
    def getSingleProductInfo(self, link):
        self.driver.get(link)
        time.sleep(3)
        title = self.getProductTitle()
        seller = self.getSeller()
        price = self.getPrice()

        if title and seller and price:
            productInfo = {
                "title": title,
                "seller": seller,
                "cost" : price,
                "link": link
            }
            return productInfo   

    def getProductTitle(self):
        try:
            return self.driver.find_element_by_id("productTitle").text.strip()
        except Exception as e:
            print("Error retrieving title for the product")
            print(e)
            return None

    def getSeller(self):
        try:
            return self.driver.find_element_by_id("sellerProfileTriggerId").text.strip()
        except Exception as e:
            print("Error retrieving seller name for the product")
            print(e)
            return None

    def getPrice(self):
        try:
            price = self.driver.find_element_by_id("priceblock_ourprice").text
            return price.strip()
        except NoSuchElementException as e:
            print("Error retrieving price for the product")
            print(e)
            return None

    def getProductsLinks(self, url):
        self.driver.get(url)
        time.sleep(3)
        try:
            results = self.driver.find_elements_by_xpath("//div[@data-asin[not(.='')]]")
            links = [config.BASE_URL+"dp/"+result.get_attribute('data-asin')+"?language=en_GB" for result in results]
            return links
        except Exception as e:
            print("Oops!!! Didn't get any product for "+config.SEARCH_TERM)
            print(e)
            return links


if __name__ == "__main__":
    amazon = AmazonAPI()
    products = amazon.run()
    MakeReport(config.SEARCH_TERM, products)
    
