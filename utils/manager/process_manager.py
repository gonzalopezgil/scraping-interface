import os
from utils.manager.file_manager import get_file_path
from exceptions.file_exceptions import FileDeletionException

def clear_process_history():
    try:
        file_path = get_file_path("processes.csv")
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        exception_text = "Error deleting process history"
        print(f"{exception_text}: {e}")
        raise FileDeletionException(exception_text)

class Column:
    def __init__(self, xpath, visual_index):
        self.xpath = xpath
        self.visual_index = visual_index
        self.first_text = None
        self.num_elements = None

    def get_xpath(self):
        return self.xpath
    
    def set_xpath(self, xpath):
        self.xpath = xpath

    def get_visual_index(self):
        return self.visual_index
    
    def set_visual_index(self, visual_index):
        self.visual_index = visual_index
    
    def get_first_text(self):
        return self.first_text
    
    def set_first_text(self, first_text):
        self.first_text = first_text
    
    def get_num_elements(self):
        return self.num_elements
    
    def set_num_elements(self, num_elements):
        self.num_elements = num_elements

class ProcessManager:
    def __init__(self):
        self.columns = []
        self.pagination_xpath = None

    def create_column(self, xpath):
        visual_index = len(self.columns) + 1
        column = Column(xpath, visual_index)
        self.columns.append(column)

    def remove_column(self, index):
        if index >= 0 and index < len(self.columns):
            self.columns.pop(index)

    def move_column(self, from_index, to_index):
        if from_index >= 0 and from_index < len(self.columns) and to_index >= 0 and to_index < len(self.columns):
            column = self.columns.pop(from_index)
            self.columns.insert(to_index, column)    

    def get_column(self, index):
        if index >= 0 and index < len(self.columns):
            return self.columns[index]
        else:
            return None
        
    def get_all_xpaths(self):
        return [column.xpath for column in self.columns]
    
    def get_all_first_texts(self):
        return [column.first_text for column in self.columns]
            
    def get_column_count(self):
        return len(self.columns)
    
    def set_first_text(self, index, text):
        column = self.get_column(index)
        if column:
            column.first_text = text

    def clear_columns(self):
        self.columns = []
