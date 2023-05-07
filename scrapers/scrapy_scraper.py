from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from .scraper import Scraper
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
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
    }

    def get_webpage(self, response):
        return Selector(response)

    def get_elements(self, xpath, obj, _=None):
        return obj.xpath(xpath)

    def close_webpage(self, _):
        # No need to close webpage with scrapy
        pass

    def start_requests(self):
        # Using a dummy website to start scrapy request
        url = "http://example.com"
        yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        if response.status != 200:
            print("Error: Status code not 200")

        obj = Selector(text=self.html)
        
        general_xpaths = [self.generalise_xpath(xpath) for xpath in self.xpaths]
        prefix = self.get_common_xpath(general_xpaths)
        elements = self.get_elements(prefix, obj)
        xpath_suffixes = self.get_suffixes(prefix, general_xpaths)

        if elements is None or len(elements) == 0:
            print("Error: No elements found")

        count = 0
        node = {label: "" for label in self.labels}
        for elem in elements:
            item = ItemLoader(self.create_class(self.labels)(), elem)
            for label,xpath in zip(self.labels, xpath_suffixes):

                item.add_xpath(label, '.'+xpath)
                if item.load_item() and label not in item.load_item():
                    item.add_value(label, "")

                if count == 0 and item.load_item():
                    if xpath.endswith('//text()'):
                        new_xpath = xpath[:-8]

                    parent_html = elem.xpath('.' + new_xpath).get()
                    target_html = elem.xpath('.' + new_xpath + '/node()').get()
                    if parent_html and target_html:
                        outer_html = parent_html.replace(target_html, "")
                        node[label] = outer_html

                if count > 0 and not item.load_item():
                    if xpath.endswith('//text()'):
                        new_xpath = xpath[:-8]

                    parent_html = elem.xpath('.' + new_xpath).get()
                    target_html = elem.xpath('.' + new_xpath + '/node()').get()
                    if not target_html:
                        target_html = ""
                    if parent_html:
                        outer_html = parent_html.replace(target_html, "")
                        if outer_html == node[label]:
                            item.add_value(label, "")

            if item.load_item():
                count+=1
                yield item.load_item()
            
            if self.max_items and count == self.max_items:
                break

        self.close_webpage(obj)

    def create_class(self, fields):
        my_dict = {field: Field() for field in fields}
        new_class = type("Element", (Item,), my_dict)
        return new_class
    
    def run_scraper(self, q, url, labels, xpaths, html, max_items):
        try:
            runner = CrawlerRunner()
            deferred = runner.crawl(ScrapyScraper, start_urls=[url], url=url, labels=labels, xpaths=xpaths, html=html, max_items=max_items)
            deferred.addBoth(lambda _: reactor.stop())

            spider = next(iter(runner.crawlers)).spider
            results = []

            def collect_items(item):
                results.append(item)

            spider.crawler.signals.connect(collect_items, signal=scrapy.signals.item_scraped)

            reactor.run()
            dict_results = self.merge_dicts(results)

            if len(dict_results) > 0:
                for label in labels:
                    elements = dict_results[label]
                    elements = self.clean_list(elements)
                    dict_results[label] = elements
            
            q.put(dict_results)
        except Exception as e:
            q.put(e)

    def scrape(self, url, labels, xpaths, html, max_items=None):
        q = Queue()
        p = Process(target=self.run_scraper, args=(q,url,labels,xpaths,html,max_items,))

        p.start()
        result = q.get()
        p.join()

        return(result)
