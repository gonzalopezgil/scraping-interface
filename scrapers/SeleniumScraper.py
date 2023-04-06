from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from . Scraper import Scraper
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

class SeleniumScraper(Scraper):

    def get_webpage(self, url, _):
        options = Options()
        options.headless = True
        options.add_argument("--window-size=1920,1200")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        return driver
    
    def get_elements(self, xpath, obj, text=None):
        xpath = self.remove_text_from_xpath(xpath)

        elements = obj.find_elements(By.XPATH, xpath)
        if text:
            try:
                WebDriverWait(obj, 10).until(lambda driver: any(text in element.text for element in elements))
                elements = [element.text for element in elements]
            except TimeoutException:
                print("Error: Text selected by the user not found in elements")
                return None

        return elements
    
    def close_webpage(self, obj):
        obj.quit()

    def remove_text_from_xpath(self, xpath):
        if xpath.endswith("//text()"):
            xpath = xpath[:-8]
        return xpath
