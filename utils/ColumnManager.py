class Column:
    def __init__(self, xpath):
        self.xpath = xpath
        self.first_text = None
        self.num_elements = None

class ColumnManager:
    def __init__(self):
        self.columns = []

    def create_column(self, xpath):
        column = Column(xpath)
        self.columns.append(column)

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