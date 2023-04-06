import requests
from bs4 import BeautifulSoup
from lxml import etree
from . Scraper import Scraper

class BeautifulSoupScraper(Scraper):

    def get_webpage(self, url, default_encoding):
        response = requests.get(url, headers=self.choose_random_header())
        soup = BeautifulSoup(response.content, "html.parser")
        dom = etree.HTML(str(soup))
        return dom

    def get_elements(self, xpath, obj, _=None):
        return obj.xpath(xpath)

    def close_webpage(self, obj):
        # No need to close webpage with beautiful soup scraper
        pass