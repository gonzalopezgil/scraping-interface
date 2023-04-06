from abc import ABC, abstractmethod
import pandas as pd
from os.path import commonprefix
import random

class Scraper(ABC):

    headers = [
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/108.0.5359.112 Mobile/15E148 Safari/604.1"},
        {"User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.128 Mobile Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.128 Mobile Safari/537.36"}
    ]

    @abstractmethod
    def get_webpage(self, url, default_encoding):
        pass

    @abstractmethod
    def get_elements(self, xpath, obj, text):
        pass

    @abstractmethod
    def close_webpage(self, obj):
        pass

    def scrape(self, url, labels, selected_text, xpaths, file_name, default_encoding=True):
        obj = self.get_webpage(url, default_encoding)

        my_dict = {}
        for xpath,label,text in zip(xpaths,labels,selected_text):
            text = self.clean_text(text)
            elements = self.get_elements(self.generalise_xpath(xpath), obj, text)
            if elements is not None and len(elements) > 0:
                elements = self.clean_list(elements)
                print(self.generalise_xpath(xpath))
                print(f"Elements: {elements}")
                if text not in elements:
                    if len(elements) > 1:
                        index = self.check_pattern(elements, text)
                        if index != -1:
                            elements = self.get_pattern(elements, text, index)
                        else:
                            # Check with other encoding
                            if default_encoding:
                                return self.scrape(url, labels, selected_text, xpaths, False)
                            else:
                                print("Error: Text selected by the user not found in elements")
                                return None
                    else:
                        print("Error: Text selected by the user not found in elements")
                        return None
                my_dict[label] = elements

        self.close_webpage(obj)

        if len(my_dict) > 0 and file_name is not None:
            df = self.dict_to_df(my_dict)
            if df is not None:
                self.save_file(df, file_name)

    def save_file(self, dataframe, file_name):
        dataframe.to_excel(file_name)

    def choose_random_header(self):
        return random.choice(self.headers)

    # Unused
    def check_encoding(self, obj, text):
        xpath = f"//*[text()='{text}']"
        if self.get_elements(xpath, obj):
            print("Encoding is correct")
        else:
            print("Encoding is not correct")

    def generalise_xpath(self, xpath):
        final_xpath = ""
        elements = str(xpath).split("/")
        ending = elements[-1]
        for i in range(len(elements)):
            elem = elements[i]
            if elem:
                if i == len(elements)-1:
                    final_xpath+="//"+ending+"//text()"
                elif "[" in elem:
                    final_xpath+="//"+elem.split("[")[0]
                else:
                    final_xpath+="/"+elem
        return final_xpath
    
    def get_suffixes(self, prefix, strings):
        if not strings:
            return []
        else:
            first_string = strings[0]
            if first_string.startswith(prefix):
                suffix = first_string[len(prefix):]
                return [suffix] + self.get_suffixes(prefix, strings[1:])
            else:
                return self.get_suffixes(prefix, strings[1:])
    
    def get_common_xpath(self, xpaths):
        if len(xpaths) == 1 and xpaths[0].endswith("//text()"):
            return xpaths[0][:-8]

        prefix = commonprefix(xpaths)

        if prefix.endswith("//"):
            prefix = prefix[:-2]
        elif prefix.endswith("["):
            prefix = prefix[:prefix.rfind("//")]

        suffixes = self.get_suffixes(prefix, xpaths)
        
        for suffix in suffixes:
            if not suffix.startswith("//") or suffix.startswith("[") or "[" in suffix.split("//")[1]:
                prefix = prefix[:prefix.rfind("//")]
                break

        return prefix
    
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

    def clean_text(self, text):
        text = text.replace("\r","").replace("\t","").replace("\n","").replace("  "," ").replace(chr(160), chr(32))
        if text == " ":
            return text
        else:
            return text.strip()
    
    def clean_list(self, elements):
        return [self.clean_text(elem) for elem in elements]
