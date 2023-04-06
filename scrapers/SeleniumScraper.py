from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from . Scraper import Scraper
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class SeleniumScraper(Scraper):

    def get_webpage(self, url, _):
        options = Options()
        options.headless = True
        options.add_argument("--window-size=1920,1200")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        return driver
    
    def get_elements(self, xpath, obj, text):
        if xpath.endswith("//text()"):
            xpath = xpath[:-8]
        
        elements = obj.find_elements(By.XPATH, xpath)
        WebDriverWait(obj, 10).until(lambda driver: any(text in element.text for element in elements))

        elements = [element.text for element in elements]
        return elements
    
    def close_webpage(self, obj):
        obj.quit()
