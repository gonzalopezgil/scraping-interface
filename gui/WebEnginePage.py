from PyQt5 import QtWebEngineWidgets

class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print("JavaScript Console Message: ", message)