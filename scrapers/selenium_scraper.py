from . scraper import Scraper
from selenium.common.exceptions import TimeoutException
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from . scraper import Scraper
import scrapy
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from multiprocessing import Process, Queue
from selenium.webdriver.support import expected_conditions as EC
import web.javascript_strings as jss
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.manager.password_manager import get_login_info_for_url
from . scrapy_selenium_scraper import ScrapySeleniumScraper
from exceptions.scraper_exceptions import ScraperStoppedException
import time

TIMEOUT = 5

class SeleniumScraper(Scraper):

    def get_driver(self):
        options = Options()

        # Avoid sending information to the server to indicate the use of an automated browser.

        # Adding argument to disable the AutomationControlled flag 
        options.add_argument("--disable-blink-features=AutomationControlled")
        # Exclude the collection of enable-automation switches 
        options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
        # Turn-off userAutomationExtension 
        options.add_experimental_option("useAutomationExtension", False) 

        options.headless = True
        options.add_argument("--window-size=1920,1200")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Changing the property of the navigator value for webdriver to undefined 
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        return driver
    
    def get_webpage(self, url):
        driver = self.get_driver()
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": UserAgent().random})
        driver.get(url)
        return driver

    def get_elements(self, xpath, obj, text=None):
        xpath = self.remove_text_from_xpath(xpath)

        elements = obj.find_elements(By.XPATH, xpath)
        if text:
            try:
                WebDriverWait(obj, TIMEOUT).until(lambda driver: any(text in element.text for element in elements))
                elements = [element.text for element in elements]
            except TimeoutException:
                print("Error: Text selected by the user not found in elements")
                return None

        return elements
    
    def close_webpage(self, obj):
        obj.quit()

    def before_scrape(self, url, labels, selected_text, xpaths, pagination_xpath, file_name, signal_manager, row, html, stop, max_pages=None):
        obj = self.get_webpage(url)
        if not self.check_elements(stop, signal_manager, row, pagination_xpath, xpaths, selected_text, url, obj):
            return
        
        general_xpaths = [self.generalise_xpath(xpath) for xpath in xpaths]
        prefix = self.get_common_xpath(general_xpaths)
        xpath_suffixes = self.get_suffixes(prefix, general_xpaths)

        pages = 0
        max_pages = max_pages if max_pages else 100
        next_page = True
        results = []

        while next_page and pages < max_pages:
            actual_html = ""
            if not pagination_xpath:
                actual_html = html
            else:
                self.infinite_scroll(obj)
                # Wait for the document to be complete (fully loaded)
                time.sleep(2)
                actual_html = obj.page_source
            
            # html, prefix, labels, xpath_suffixes, selected_text, file_name, row, signal_manager
            dictionary = self.scrape(actual_html, prefix, labels, xpath_suffixes)
            print(f"Dictionary after scrape: {dictionary}")
            results.append(dictionary)

            if pagination_xpath:
                try:
                    WebDriverWait(obj, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, pagination_xpath)))
                    next_button = obj.find_element(By.XPATH, pagination_xpath)
                    next_button.click()
                except Exception:
                    print("Error: Pagination button not found")
                    next_page = False
            else:
                next_page = False
            pages+=1

        if pagination_xpath:
            self.close_webpage(obj)

        print(f"Results at the end of the scraping: {results}")

        self.after_scrape(results, labels, selected_text, file_name, row, signal_manager)

    def after_scrape(self, results, labels, selected_text, file_name, row, signal_manager):
        dict_results = self.merge_list_dicts(results)
        print(dict_results)
        if len(dict_results) > 0:
            for label,text in zip(labels, selected_text):
                elements = dict_results[label]
                elements = self.clean_list(elements)
                text = self.clean_text(text)
                #if text not in elements:
                #    index = self.check_pattern(elements, text)
                #    if index != -1:
                #        elements = self.get_pattern(elements, text, index)
                #    else:
                #        print("Error: Text selected by the user not found in elements")
                #        return None
                dict_results[label] = elements
            
            df = self.dict_to_df(dict_results)

            if df is not None and file_name is not None:
                self.save_file(df, file_name)
                signal_manager.process_signal.emit(row, "Finished", file_name)
        else:
            print("Error: No elements found")
            signal_manager.process_signal.emit(row, "Error", "")



    def run_scraper(self, q, html, prefix, labels, xpath_suffixes):
        try:
            runner = CrawlerRunner()
            deferred = runner.crawl(ScrapySeleniumScraper, start_urls=["http://localhost:8000"], html=html, prefix=prefix, labels=labels, xpath_suffixes=xpath_suffixes)
            deferred.addBoth(lambda _: reactor.stop())

            spider = next(iter(runner.crawlers)).spider

            def collect_items(item):
                dictionary = dict(item)
                q.put(dictionary)

            spider.crawler.signals.connect(collect_items, signal=scrapy.signals.item_scraped)

            reactor.run()

            q.put(None)

        except Exception as e:
            print(f"Error: {e}")
            q.put(None)
    
    def scrape(self, html, prefix, labels, xpath_suffixes):
        q = Queue()
        p = Process(target=self.run_scraper, args=(q,html,prefix,labels,xpath_suffixes))

        results = []
        p.start()
        data = q.get()
        if data:
            data = dict(data)
        while data:
            results.append(data)
            data = q.get()
            if data:
                data = dict(data)
        p.join()

        return results
        

    def remove_text_from_xpath(self, xpath):
        if xpath.endswith("//text()"):
            xpath = xpath[:-8]
        return xpath
    
    def login_using_stored_credentials(self, driver, login_info):
        try:
            driver.get(login_info["url"])

            # Find and fill in the email or username input
            email_or_text_input = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, '//input[@type="text"]|//input[@type="email"]'))
            )
            email_or_text_input.send_keys(login_info["username"])

            # Find and fill in the password input
            password_input = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, '//input[@type="password"]'))
            )
            
            if not password_input:
                print("Not password input found")
                # Click the form button and wait for the password input to appear
                self.click_form_button(driver)

                password_input = WebDriverWait(driver, TIMEOUT).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@type="password"]'))
                )
                password_input.send_keys(login_info["password"])
                self.click_form_button(driver)

            else:
                print("Password input found")
                password_input.send_keys(login_info["password"])
                print("Keys sent")
                self.click_form_button(driver)

        except Exception:
            print("Couldn't find the email or username input or the password input.")

    def click_form_button(self, driver):
        try:
            print("looking for form button")
            button_xpath = driver.execute_script(jss.FIND_RELATED_BUTTON_JS)
            print(button_xpath)

            if button_xpath:
                print("Button found")
                # Find the button using its XPath and click it
                button = driver.find_element(By.XPATH, button_xpath)
                button.click()
            else:
                print("Couldn't find a related button to click.")
        except Exception:
            print("Couldn't find a related button to click.")

    def check_for_captcha(self, obj):
        # Look for CAPTCHA in iframes
        iframes = self.get_elements("//iframe[@title='reCAPTCHA']", obj)
        if iframes is not None and len(iframes) > 0:
            return True
        return False
    
    def check_elements(self, stop, signal_manager, row, pagination_xpath, xpaths, selected_text, url, obj=None):
        #self.pagination_xpath = "//a[contains(text(), 'Next') or contains(text(), 'next') or contains(text(), 'NEXT')]"
        self.update_progress("1%", stop, signal_manager, row)

        # Check if elements are present when pagination_xpath exists
        elements_present = True
        if pagination_xpath:
            for xpath, text in zip(xpaths, selected_text):
                text = self.clean_text(text)
                elements = self.get_elements(self.generalise_xpath(xpath), obj, text)
                if elements is None or len(elements) == 0:
                    elements_present = False
                    break

        # If elements don't exist, execute login_using_stored_credentials and try again
        if not elements_present:
            login_info = get_login_info_for_url(url)
            if login_info:
                self.login_using_stored_credentials(obj, login_info)

                for xpath, text in zip(xpaths, selected_text):
                    text = self.clean_text(text)
                    elements = self.get_elements(self.generalise_xpath(xpath), obj, text)
                    if elements is not None and len(elements) > 0:
                        elements = self.clean_list(elements)
                        elements = self.find_text_in_data(elements, text)
                        if elements is None:
                            print("Error: Text selected by the user not found in elements")
                            return False

        self.update_progress("50%", stop, signal_manager, row)
        print("Selenium found elements")
        return True
    
    def update_progress(self, progress, stop, signal_manager, row):
        if stop.value:
            signal_manager.process_signal.emit(row, "Stopped", "")
            raise ScraperStoppedException("Scraper stopped by the user")
        signal_manager.process_signal.emit(row, progress, "")

    def infinite_scroll(self, obj):
        # scroll down repeatedly
        while True:
            # scroll down to the bottom of the page
            obj.execute_script('window.scrollTo(0, document.body.scrollHeight);')

            # wait for the page to load new content
            obj.implicitly_wait(TIMEOUT)

            # check if we have reached the end of the page
            end_of_page = obj.execute_script('return window.pageYOffset + window.innerHeight >= document.body.scrollHeight;')
            if end_of_page:
                break
