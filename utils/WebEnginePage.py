from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import pyqtSlot

class WebEnginePage(QWebEnginePage):
    
    def __init__(self, parent=None, table_widget=None, table_xpath=None, process_manager=None):
        super().__init__(parent)
        self.table_widget = table_widget
        self.table_xpath = table_xpath
        self.process_manager = process_manager
        self.pagination_clicked = False

    def javaScriptConsoleMessage(self, level, message, line_number, source_id):
        if not message.startswith("To Python>"):
            print(f"JavaScript Message: {message}")
        else:
            text = message.split(">")
            message_type = text[1]
            value = text[2]
            if message_type == "selectedText" and not self.pagination_clicked:
                row = int(text[3])
                col = self.process_manager.get_column_count() - 1
                if row == 1:
                    self.process_manager.get_column(col).set_first_text(value)
                if self.table_widget.rowCount() < row:
                    self.table_widget.setRowCount(row)
                self.table_widget.setItem(row-1, col, QTableWidgetItem(value))
            elif message_type == "xpath" and not self.pagination_clicked:
                self.process_manager.create_column(value)
                if self.table_xpath.rowCount() < 1:
                    self.table_xpath.setRowCount(1)
                count = self.process_manager.get_column_count()
                if self.table_widget.columnCount() < count:
                    self.table_widget.setColumnCount(count)
                    self.table_xpath.setColumnCount(count)
                col = count - 1
                self.table_xpath.setItem(0, col, QTableWidgetItem(value))
            elif message_type == "xpathRel" and self.pagination_clicked:
                self.process_manager.pagination_xpath = value

    @pyqtSlot()
    def on_pagination_button_clicked(self):
        self.pagination_clicked = not self.pagination_clicked

    