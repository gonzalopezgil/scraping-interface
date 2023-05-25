from . scraper import Scraper
import scrapy
from scrapy.loader import ItemLoader
from scrapy.item import Item, Field
from scrapy.selector import Selector

TIMEOUT = 5

class ScrapySeleniumScraper(Scraper, scrapy.Spider):
    name = "ScrapySeleniumScraper"

    custom_settings = {
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
        'DOWNLOADER_MIDDLEWARES': {
            'scrapers.middlewares.NoInternetMiddleware': 1,
            'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': None,
            'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': None,
            'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': None,
            'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': None,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': None,
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': None,
            'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
            'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
            'scrapy.downloadermiddlewares.stats.DownloaderStats': None,
            'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': None,
        },
    }

    def __init__(self, stop=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stop = stop

    def get_driver(self):
        pass
    
    def get_webpage(self, url):
        pass

    def get_elements(self, xpath, obj, text=None):
        pass
    
    def close_webpage(self, obj):
        pass

    # html, prefix, labels, xpath_suffixes
    def parse(self, response):
        sel = Selector(text=self.html)
        elements = sel.xpath(self.prefix)


        for elem in elements:
            item = ItemLoader(self.create_class(self.labels)(), elem)
            for label,xpath in zip(self.labels, self.xpath_suffixes):
                item.add_xpath(label, '.'+xpath)
                if item.load_item() and label not in item.load_item():
                    item.add_value(label, "")

            if item.load_item():
                yield item.load_item()

    def create_class(self, fields):
        my_dict = {field: Field() for field in fields}
        new_class = type("Element", (Item,), my_dict)
        return new_class
