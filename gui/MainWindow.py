from PyQt5.QtWidgets import QMainWindow, QTabWidget
from gui.BrowserTab import BrowserTab
from gui.ProcessesTab import ProcessesTab
from gui.SettingsTab import SettingsTab
from gui.SeleniumScraper import SeleniumScraper
import threading
from gui.SignalManager import SignalManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scraping Interface")
        self.resize(1800, 1000)

        # Create a QTabWidget to hold the tabs
        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)
        
        # Create the tabs
        self.browser_tab = BrowserTab(self)
        self.processes_tab = ProcessesTab(self)
        self.settings_tab = SettingsTab(self)

        foo = SignalManager()
        foo.fooSignal.connect(self.processes_tab.update_status)

        self.browser_tab.download_button.clicked.connect(lambda: self.processes_tab.add_row(self.browser_tab.browser.url().toString()))
        self.browser_tab.download_button.clicked.connect(lambda: threading.Thread(target=self.thread_function, args=(self.browser_tab.browser.url().toString(), self.browser_tab.get_table_data(), foo, self.processes_tab.table.rowCount()-1), daemon=True).start())

        # Add the tabs to the tab widget
        self.tabs.addTab(self.browser_tab, "Browser")
        self.tabs.addTab(self.processes_tab, "Processes")
        self.tabs.addTab(self.settings_tab, "Settings")

    def thread_function(self, url, table_data, obj, row):
        self.tabs.setCurrentIndex(1)
        scraper = SeleniumScraper()
        scraper.scrape(url, table_data[0], table_data[2])
        obj.fooSignal.emit(row, "Finished")