from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from . Scraper import Scraper
from scrapy.crawler import CrawlerProcess
import scrapy

class ScrapyScraper(Scraper, Spider):
    name = "ScrapyScraper"

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36'
    }    

    def get_webpage(self, response, _):
        return Selector(response)

    def get_elements(self, xpath, obj, _=None):
        return obj.xpath(xpath)

    def close_webpage(self, _):
        # No need to close webpage with scrapy
        pass

    def parse(self, response):
        obj = self.get_webpage(response, self.default_encoding)
        
        general_xpaths = [self.generalise_xpath(xpath) for xpath in self.xpaths]
        prefix = self.get_common_xpath(general_xpaths)
        elements = self.get_elements(prefix, obj)
        xpath_suffixes = self.get_suffixes(prefix, general_xpaths)

        for elem in elements:
            item = ItemLoader(self.create_class(self.labels)(), elem)
            for label,xpath in zip(self.labels, xpath_suffixes):
                item.add_xpath(label, '.'+xpath)
                if item.load_item() and label not in item.load_item():
                    item.add_value(label, "")

            if item.load_item():
                yield item.load_item()

    def create_class(self, fields):
        my_dict = {field: Field() for field in fields}
        new_class = type("Element", (Item,), my_dict)
        return new_class
    
    def scrape(self, url, labels, selected_text, xpaths, file_name, default_encoding=True):
        process = CrawlerProcess()
        process.crawl(ScrapyScraper, start_urls=[url], labels=labels, selected_text=selected_text, xpaths=xpaths, default_encoding=default_encoding)
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
                if text not in elements:
                    index = self.check_pattern(elements, text)
                    if index != -1:
                        elements = self.get_pattern(elements, text, index)
                    else:
                        print("Error: Text selected by the user not found in elements")
                        return None
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
