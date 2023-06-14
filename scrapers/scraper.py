from abc import ABC, abstractmethod
import pandas as pd
from os.path import commonprefix
import xml.etree.ElementTree as ET
import os
import logging
from scrapy.item import Item, Field
from utils.manager.file_manager import get_folder_path

logger = logging.getLogger(__name__)

class Scraper(ABC):

    @abstractmethod
    def get_webpage(self, url):
        pass

    @abstractmethod
    def get_elements(self, xpath, obj, text=None):
        pass

    def create_class(self, fields):
        my_dict = {field: Field() for field in fields}
        new_class = type("Element", (Item,), my_dict)
        return new_class

    def find_text_in_data(self, elements, text):
        if text not in elements:
            if len(elements) > 1:
                index = self.check_pattern(elements, text)
                if index != -1:
                    elements = self.get_pattern(elements, text, index)
                else:
                    return None
            else:
                return None
        else:
            return elements

    def save_file(self, dataframe, file_name):
        _, file_extension = os.path.splitext(file_name)
        file_extension = file_extension.lower()

        if file_extension == ".xlsx":
            dataframe.to_excel(file_name)
        elif file_extension == ".csv":
            dataframe.to_csv(file_name, index=False, encoding="utf-8-sig")
        elif file_extension == ".json":
            dataframe.to_json(file_name, orient="records")
        elif file_extension == ".xml":
            root = ET.Element("root")
            for index, row in dataframe.iterrows():
                item = ET.SubElement(root, "item")
                for col_name, value in row.items():
                    col = ET.SubElement(item, col_name)
                    col.text = str(value)

            tree = ET.ElementTree(root)
            tree.write(file_name, encoding="utf-8", xml_declaration=True)
        else:
            logger.error(f"Error: unsupported file format: {file_extension}")

    def generalise_xpath(self, xpath):
        final_xpath = ""
        elements = str(xpath).split("/")
        ending = elements[-1]
        for i in range(len(elements)):
            elem = elements[i]
            if elem:
                if i == len(elements)-1:
                    final_xpath+="//"+ending+"//text()"
                else:
                    final_xpath+="//"+elem
        return final_xpath
    
    def get_suffixes(self, prefix, strings):
        if not strings:
            return []
        elif prefix == "/html/body":
            return strings
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
            if not suffix.startswith("//") or suffix.startswith("[") or "[" in suffix.split("//")[0]:
                prefix = prefix[:prefix.rfind("//")]
                break

        if len(xpaths) > 1 and prefix == "":
            return "/html/body"

        return prefix
    
    def dict_to_df(self, my_dict):
        try:
            df = pd.DataFrame(my_dict)
            df.index += 1
            return df
        except ValueError as e:
            logger.error(f"Error creating dataframe: {e}")
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
    
    def merge_dicts(self, dicts):
        result = {}
        for d in dicts:
            for k, v in d.items():
                item = [' '.join(v)]
                if k in result:
                    if isinstance(result[k], list):
                        result[k].extend(item)
                    else:
                        result[k] = [result[k]] + item
                else:
                    result[k] = item
        return result
    
    def merge_list_dicts(self, lists_of_dicts):
        result = {}
        for dict_list in lists_of_dicts:
            for d in dict_list:
                for k, v in d.items():
                    item = [' '.join(v)]
                    if k in result:
                        if isinstance(result[k], list):
                            result[k].extend(item)
                        else:
                            result[k] = [result[k]] + item
                    else:
                        result[k] = item
        return result
    
    def set_logs(self, file_name):
        # Set up root logger
        scrapy_logger = logging.getLogger()
        scrapy_logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(f"{get_folder_path('logs')}/{file_name}.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        scrapy_logger.addHandler(file_handler)

