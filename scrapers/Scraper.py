from abc import ABC, abstractmethod
import pandas as pd

class Scraper(ABC):

    @abstractmethod
    def scrape(self, url, labels, xpaths):
        pass

    @abstractmethod
    def get_elements(self, xpath, obj):
        pass

    def generalise_xpath(self, xpath):
        final_xpath = ""
        elements = str(xpath).split("/")
        ending = elements[-1]
        for elem in elements:
            if elem:
                if elem == ending:
                    final_xpath+="//"+ending
                elif "[" in elem:
                    final_xpath+="//"+elem.split("[")[0]
                else:
                    final_xpath+="/"+elem
        return final_xpath
    
    def dict_to_df(self, my_dict):
        df = pd.DataFrame(my_dict)
        df.index += 1

        return df