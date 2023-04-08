from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWidgets import QTableWidgetItem

class WebEnginePage(QWebEnginePage):
    table_widget = None
    last_column = -1

    def reset_table(self):
        self.last_column = -1

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if not message.startswith("To Python>"):
            print(f"JavaScript Message: {message}")
        else:
            text = message.split(">")
            message_type = text[1]
            value = text[2]
            if message_type == "selectedText":
                row = int(text[3])
                print(message_type,value,row)
                if self.table_widget.rowCount() < row:
                    self.table_widget.setRowCount(row)
                self.table_widget.setItem(row-1, self.last_column, QTableWidgetItem(value))
            elif message_type == "xpath":
                print(f"XPath: {value}")
                self.last_column += 1
    