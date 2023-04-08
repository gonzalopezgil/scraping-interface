from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWidgets import QTableWidgetItem

class WebEnginePage(QWebEnginePage):
    
    def __init__(self, parent=None, table_widget=None, column_manager=None):
        super().__init__(parent)
        self.table_widget = table_widget
        self.column_manager = column_manager

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if not message.startswith("To Python>"):
            print(f"JavaScript Message: {message}")
        else:
            text = message.split(">")
            message_type = text[1]
            value = text[2]
            if message_type == "selectedText":
                row = int(text[3])
                col = self.column_manager.get_column_count() - 1
                if row == 1:
                    self.column_manager.set_first_text(col, value)
                if self.table_widget.rowCount() < row:
                    self.table_widget.setRowCount(row)
                self.table_widget.setItem(row-1, col, QTableWidgetItem(value))
            elif message_type == "xpath":
                self.column_manager.create_column(value)
    