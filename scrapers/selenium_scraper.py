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
from utils.manager.password_manager import get_login_info
from . scrapy_selenium_scraper import ScrapySeleniumScraper
from exceptions.scraper_exceptions import ScraperStoppedException
import time
import random

TIMEOUT = 5
XPATH_USERNAME = '//input[@type="text"]|//input[@type="email"]'
XPATH_PASSWORD = '//input[@type="password"]'

class SeleniumScraper(Scraper):

    def get_driver(self, headless=True):
        options = Options()

        # Avoid sending information to the server to indicate the use of an automated browser.

        # Adding argument to disable the AutomationControlled flag 
        options.add_argument("--disable-blink-features=AutomationControlled")
        # Exclude the collection of enable-automation switches 
        options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
        # Turn-off userAutomationExtension 
        options.add_experimental_option("useAutomationExtension", False) 

        options.headless = headless
        options.add_argument("--window-size=1920,1200")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Changing the property of the navigator value for webdriver to undefined 
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        return driver
    
    def get_webpage(self, url, headless=True):
        driver = self.get_driver(headless)
        #user_agent = UserAgent().random
        user_agent = self.get_random_chrome_ua()
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": user_agent})
        driver.get(url)
        return driver

    def get_elements(self, xpath, obj, text=None):
        xpath = self.remove_text_from_xpath(xpath)
        try:
            WebDriverWait(obj, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, xpath)))
            elements = obj.find_elements(By.XPATH, xpath)
            if text:
                WebDriverWait(obj, TIMEOUT).until(lambda driver: any(text in element.text for element in elements))
                elements = [element.text for element in elements]
            return elements
        except TimeoutException:
            print("Error: Text selected by the user not found in elements")
            return None
    
    def close_webpage(self, obj):
        obj.quit()

    def before_scrape(self, url, labels, selected_text, xpaths, pagination_xpath, file_name, signal_manager, row, html, stop, interaction, max_pages=None):
        self.update_progress("1%", stop, signal_manager, row)
        if pagination_xpath:
            obj = self.get_webpage(url)
            obj = self.check_elements(stop, signal_manager, row, xpaths, selected_text, url, obj, interaction)
            if obj is None:
                return
        
        self.update_progress("5%", stop, signal_manager, row)

        general_xpaths = [self.generalise_xpath(xpath) for xpath in xpaths]
        prefix = self.get_common_xpath(general_xpaths)
        xpath_suffixes = self.get_suffixes(prefix, general_xpaths)

        pages = 0
        max_pages = max_pages if max_pages else 100
        next_page = True
        results = []

        while next_page and pages < max_pages:

            self.update_progress("10%", stop, signal_manager, row)

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
            self.update_progress(f"{10+(pages/max_pages)*80}%", stop, signal_manager, row)

        if pagination_xpath:
            self.close_webpage(obj)

        self.after_scrape(results, labels, selected_text, file_name, row, signal_manager)

    def after_scrape(self, results, labels, selected_text, file_name, row, signal_manager):
        dict_results = self.merge_list_dicts(results)
        if len(dict_results) > 0:
            for label,text in zip(labels, selected_text):
                elements = dict_results[label]
                elements = self.clean_list(elements)
                text = self.clean_text(text)
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
    
    def find_login_input(self, obj, xpath):
        try:
            login_input = WebDriverWait(obj, TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return login_input != None
        except Exception:
            print("Couldn't find the email or username input.")

    def fill_input(self, obj, xpath, text):
        try:
            login_input = WebDriverWait(obj, TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            if login_input:
                login_input.send_keys(text)
                print("Login input filled")
                return True
            else:
                print("Error: Login input not found")
                return False
        except Exception:
            print("Error: Login input not filled")
            return False
    
    def login_using_stored_credentials(self, driver, url, stop, signal_manager, row, interaction, login_info=None):
        try:
            login_url = url
            if login_info:
                login_url = login_info["url"]
            driver.get(login_url)

            # Find and fill in the email or username input

            if not self.find_login_input(driver, XPATH_USERNAME):
                print("Not login form found")
                return False
            
            driver = self.require_user_interaction(driver, login_url, stop, signal_manager, row, interaction)

            if self.find_login_input(driver, XPATH_USERNAME):

                if login_info:
                    self.fill_input(driver, XPATH_USERNAME, login_info["username"])
                    self.fill_input(driver, XPATH_PASSWORD, login_info["password"])

                # Wait for the user to login
                interaction.wait()
                interaction.clear()

            cookies = driver.get_cookies()
                
            driver.quit()
            driver = self.get_webpage(url)
            for cookie in cookies:
                driver.add_cookie(cookie)
            driver.get(url)
            return driver

        except Exception:
            print("Couldn't find the email or username input or the password input.")
            return None

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
    
    def _check_elements(self, xpaths, selected_text, obj):
        for xpath, text in zip(xpaths, selected_text):
            text = self.clean_text(text)
            elements = self.get_elements(self.generalise_xpath(xpath), obj, text)
            if elements is None or len(elements) == 0:
                return False
        return True
    
    def require_user_interaction(self, obj, url, stop, signal_manager, row, interaction, captcha=False):
        # Save cookies
        cookies = obj.get_cookies()

        # Quit the headless driver
        obj.quit()

        self.update_progress("Requires interaction", stop, signal_manager, row)
        # Wait for the user to open the Selenium window
        interaction.wait()
        interaction.clear()

        # Start a new driver without headless mode
        obj = self.get_webpage(url, headless=False)

        if captcha:
            # Add the cookies to the new driver
            for cookie in cookies:
                obj.add_cookie(cookie)

        # Refresh to apply the cookies
        obj.refresh()

        return obj
    
    def check_elements(self, stop, signal_manager, row, xpaths, selected_text, url, obj, interaction):
        if not self._check_elements(xpaths, selected_text, obj) and self.check_for_captcha(obj):
            print("CAPTCHA found")
            
            obj = self.require_user_interaction(obj, url, stop, signal_manager, row, interaction, True)

            if self.check_for_captcha(obj):
                # Wait for the user to solve the CAPTCHA
                interaction.wait()
                interaction.clear()
        else:
            print("No CAPTCHA found")

        # Check if login is required
        if not self._check_elements(xpaths, selected_text, obj):
            obj = self.login_using_stored_credentials(obj, url, stop, signal_manager, row, interaction, get_login_info(url))
            if obj:
                for xpath, text in zip(xpaths, selected_text):
                    text = self.clean_text(text)
                    elements = self.get_elements(self.generalise_xpath(xpath), obj, text)
                    if elements is not None and len(elements) > 0:
                        elements = self.clean_list(elements)
                        elements = self.find_text_in_data(elements, text)
                        if elements is None:
                            print("Error: Text selected by the user not found in elements")
                            return None
        return obj
    
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

    def get_random_chrome_ua(self):
        version = str(random.randint(80, 90))
        platforms = [
            '(Windows NT 10.0; Win64; x64)',  # Windows 10
            '(Macintosh; Intel Mac OS X 10_15_4)',  # Mac OS X
            '(X11; Linux x86_64)',  # Linux
            '(Android 10; Mobile)',  # Android
            '(iPhone; CPU iPhone OS 13_3 like Mac OS X)',  # iPhone
        ]
        platform = random.choice(platforms)
        return f"Mozilla/5.0 {platform} AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36"
    
    def check_for_captcha(self, obj):
        # Look for CAPTCHA in iframes
        iframes = self.get_elements("//iframe[@title='reCAPTCHA']", obj)
        if iframes is not None and len(iframes) > 0:
            # Display the Selenium window for user interaction
            obj.set_window_position(0, 0)
            obj.set_window_size(800, 600)
            return True
        return False
