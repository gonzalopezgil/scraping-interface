from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
from . Scraper import Scraper

class SeleniumScraper(Scraper):

    def init_driver(self):
        options = Options()
        options.headless = True
        options.add_argument("--window-size=1920,1200")
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def get_elements(self, xpath, driver):
        return driver.find_elements(By.XPATH, xpath)
    
    def scrape(self, url, labels, xpaths):
        driver = self.init_driver()
        driver.get(url)

        my_dict = {}
        for xpath,label in zip(xpaths,labels):
            elements = self.get_elements(self.generalise_xpath(xpath),driver)
            # print(list(map(lambda x: x.text, elements)))
            my_dict[label] = list(map(lambda x: x.text, elements))
        
        df = pd.DataFrame(my_dict)
        df.index += 1
        
        driver.quit()
        
        return df