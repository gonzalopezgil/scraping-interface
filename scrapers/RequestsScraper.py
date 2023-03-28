import requests
from lxml import html
from . Scraper import Scraper

class RequestsScraper(Scraper):

    def get_elements(self, xpath, obj):
        return obj.xpath(xpath)

    def scrape(self, url, labels, xpaths):
        response = requests.get(url)
        tree = html.fromstring(response.text) 

        my_dict = {}
        for xpath,label in zip(xpaths,labels):
            elements = self.get_elements(self.generalise_xpath(xpath), tree)
            my_dict[label] = list(map(lambda x: x.text, elements))

        return self.dict_to_df(my_dict)