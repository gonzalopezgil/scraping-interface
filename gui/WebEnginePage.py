from PyQt5.QtWebEngineWidgets import QWebEnginePage

class WebEnginePage(QWebEnginePage):

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print("JavaScript Console Message: ", message)