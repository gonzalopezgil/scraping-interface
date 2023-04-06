import requests
from lxml import html
from . Scraper import Scraper

class RequestsScraper(Scraper):

    def get_webpage(self, url, default_encoding):
        response = requests.get(url, headers=self.choose_random_header())
        if default_encoding:
            content = response.content
        else:
            content = response.text
        tree = html.fromstring(content)
        return tree

    def get_elements(self, xpath, obj, _):
        return obj.xpath(xpath)
    
    def close_webpage(self, _):
        # No need to close webpage with requests scraper
        pass
