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
                    final_xpath+="//"+ending+"//text()"
                elif "[" in elem:
                    final_xpath+="//"+elem.split("[")[0]
                else:
                    final_xpath+="/"+elem
        return final_xpath
    
    def dict_to_df(self, my_dict):
        try:
            df = pd.DataFrame(my_dict)
            df.index += 1
            return df
        except ValueError as e:
            print(f"Error creating dataframe: {e}")
            return None
        
    def __get_pattern(self, index, elem, elements, selected_text):
        if elem == selected_text:
            return index
        else:
            if selected_text.startswith(elem):
                return self.__get_pattern(index+1, elem + elements[index+1], elements, selected_text)
            else:
                return None
            
    def get_pattern(self, elements, selected_text, first_index):
        last_index = self.__get_pattern(first_index, elements[first_index], elements, selected_text)
        index = last_index - first_index
        new_elements = []
        while len(elements) > 0:
            pattern = ''.join(elements[:index+1])
            new_elements.append(pattern)
            elements = elements[index+1:]
        return new_elements
    
    def check_pattern(self, elements, selected_text):
        i = 0
        while i < len(elements):
            if selected_text.startswith(elements[i]):
                return i
            i+=1
        return -1
