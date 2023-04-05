from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWidgets import QTableWidgetItem
import pyperclip

class WebEnginePage(QWebEnginePage):
    table_widget = None
    last_column = -1
    clicked_xpath = None
    clicked_text = ""

    def reset_table(self):
        self.last_column = -1
        self.clicked_xpath = None

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print(f"JavaScript Message: {message}")
        text = pyperclip.paste()
        if message.startswith("/html") and message != self.clicked_xpath and text != self.clicked_text:
            if self.table_widget.rowCount() == 1:
                self.table_widget.insertRow(1)
            self.last_column += 1
            self.table_widget.setItem(1, self.last_column, QTableWidgetItem(message))
            self.clicked_xpath = message
            self.clicked_text = text
        