from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from . Scraper import Scraper
from scrapy.crawler import CrawlerRunner
import scrapy
from twisted.internet import reactor
from multiprocessing import Process, Queue

class ScrapyScraper(Scraper, Spider):
    name = "ScrapyScraper"

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36',
        'CONCURRENT_REQUESTS': 32,
        'DOWNLOAD_DELAY': 0.5,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 16,
        'AUTOTHROTTLE_MAX_DELAY': 5.0,
        'AUTOTHROTTLE_DEBUG': True,
        'CLOSESPIDER_ITEMCOUNT': 5,
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

        count = 0
        for elem in elements:
            item = ItemLoader(self.create_class(self.labels)(), elem)
            for label,xpath in zip(self.labels, xpath_suffixes):
                item.add_xpath(label, '.'+xpath)
                if item.load_item() and label not in item.load_item():
                    item.add_value(label, "")

            if item.load_item():
                count+=1
                yield item.load_item()
            
            if count == 5:
                break

        self.close_webpage(obj)

    def create_class(self, fields):
        my_dict = {field: Field() for field in fields}
        new_class = type("Element", (Item,), my_dict)
        return new_class
    
    def f(self, q, url, labels, selected_text, xpaths, default_encoding=True):
        try:
            runner = CrawlerRunner()
            deferred = runner.crawl(ScrapyScraper, start_urls=[url], url=url, labels=labels, selected_text=selected_text, xpaths=xpaths, default_encoding=default_encoding, preview=True)
            deferred.addBoth(lambda _: reactor.stop())

            spider = next(iter(runner.crawlers)).spider
            results = []

            def collect_items(item):
                results.append(item)

            spider.crawler.signals.connect(collect_items, signal=scrapy.signals.item_scraped)

            reactor.run()
            dict_results = self.merge_dicts(results)
            q.put(dict_results)
        except Exception as e:
            q.put(e)

    def preview_scrape(self, url, labels, selected_text, xpaths, default_encoding=True):
        q = Queue()
        p = Process(target=self.f, args=(q,url,labels,selected_text,xpaths,default_encoding,))

        p.start()
        result = q.get()
        p.join()

        return(result)
