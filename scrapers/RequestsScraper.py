import requests
from lxml import html
from . Scraper import Scraper

class RequestsScraper(Scraper):

    def get_elements(self, xpath, obj):
        return obj.xpath(xpath)

    def scrape(self, url, labels, selected_text, xpaths):
        response = requests.get(url)
        tree = html.fromstring(response.content)

        my_dict = {}
        for xpath,label,text in zip(xpaths,labels,selected_text):
            elements = self.get_elements(self.generalise_xpath(xpath), tree)
            if text != elements[0]:
                elements = self.get_pattern(elements, text)
            my_dict[label] = elements

        return self.dict_to_df(my_dict)