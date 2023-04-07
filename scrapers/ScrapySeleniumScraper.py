from . Scraper import Scraper
import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from scrapy.loader import ItemLoader
from scrapy.item import Item, Field
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector

class ScrapySeleniumScraper(Scraper, scrapy.Spider):
    name = "ScrapySeleniumScraper"

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

    def start_requests(self):
        # Using a dummy website to start scrapy request
        url = "http://quotes.toscrape.com"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        obj = self.get_webpage(self.url, self.default_encoding)
        
        general_xpaths = [self.generalise_xpath(xpath) for xpath in self.xpaths]
        prefix = self.get_common_xpath(general_xpaths)
        elements = self.get_elements(prefix, obj)
        xpath_suffixes = self.get_suffixes(prefix, general_xpaths)

        print(f"Prefix: {prefix}")
        print(f"Suffixes: {xpath_suffixes}")
        print(f"Elements: {len(elements)}")

        for xpath,label,text in zip(self.xpaths,self.labels,self.selected_text):
            text = self.clean_text(text)
            elements = self.get_elements(self.generalise_xpath(xpath), obj, text)
            if elements is not None and len(elements) > 0:
                elements = self.clean_list(elements)
                print(self.generalise_xpath(xpath))
                print(f"Elements ({len(elements)})")
                elements = self.find_text_in_data(elements, text)
                if elements is None:
                    print("Error: Text selected by the user not found in elements")
                    return None

        sel = Selector(text=obj.page_source)
        elements = sel.xpath(prefix)

        for elem in elements:
            item = ItemLoader(self.create_class(self.labels)(), elem)
            for label,xpath in zip(self.labels, xpath_suffixes):
                item.add_xpath(label, '.'+xpath)
                if item.load_item() and label not in item.load_item():
                    item.add_value(label, "")

            if item.load_item():
                yield item.load_item()
        
        self.close_webpage(obj)

    def create_class(self, fields):
        my_dict = {field: Field() for field in fields}
        new_class = type("Element", (Item,), my_dict)
        return new_class
    
    def scrape(self, url, labels, selected_text, xpaths, file_name, default_encoding=True):
        process = CrawlerProcess()
        process.crawl(ScrapySeleniumScraper, start_urls=["http://quotes.toscrape.com"], url=url, labels=labels, selected_text=selected_text, xpaths=xpaths, default_encoding=default_encoding)
        spider = next(iter(process.crawlers)).spider
        results = []

        def collect_items(item):
            results.append(item)

        spider.crawler.signals.connect(collect_items, signal=scrapy.signals.item_scraped)
        process.start()
        process.join()

        dict_results = self.merge_dicts(results)

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
    
    def merge_dicts(self, dict_list):
        result = {}
        for d in dict_list:
            for k, v in d.items():
                if k in result:
                    if isinstance(result[k], list):
                        result[k].extend(v)
                    else:
                        result[k] = [result[k]] + v
                else:
                    result[k] = v
        return result
    
    def remove_text_from_xpath(self, xpath):
        if xpath.endswith("//text()"):
            xpath = xpath[:-8]
        return xpath