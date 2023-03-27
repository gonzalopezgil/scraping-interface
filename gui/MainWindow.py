from PyQt5.QtWidgets import QMainWindow, QTabWidget, QMessageBox
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

        self.foo = SignalManager()
        self.foo.fooSignal.connect(self.processes_tab.update_status)

        self.thread = None

        self.browser_tab.download_button.clicked.connect(lambda: self.processes_tab.add_row(self.browser_tab.browser.url().toString()))
        self.browser_tab.download_button.clicked.connect(lambda: self.start_thread(self.browser_tab.browser.url().toString(), self.browser_tab.get_table_data(), self.foo, self.processes_tab.table.rowCount()-1))

        # Add the tabs to the tab widget
        self.tabs.addTab(self.browser_tab, "Browser")
        self.tabs.addTab(self.processes_tab, "Processes")
        self.tabs.addTab(self.settings_tab, "Settings")

    def start_thread(self, url, data, foo, row):
        self.thread = threading.Thread(target=self.thread_function, args=(url, data, foo, row), daemon=True)
        self.thread.start()

    def thread_function(self, url, table_data, obj, row):
        self.tabs.setCurrentIndex(1)
        scraper = SeleniumScraper()
        scraper.scrape(url, table_data[0], table_data[2])
        obj.fooSignal.emit(row, "Finished")
        self.processes_tab.save_data()

    def closeEvent(self, event):
        if self.thread and self.thread.is_alive():
            # Display a message box with a "Force Stop" button
            reply = QMessageBox.question(self, "Warning", "The thread is still running. Do you want to force it to stop?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                # Call a method that stops the thread
                self.stop_thread()
                # Accept the close event and close the application
                event.accept()
            else:
                # Ignore the close event
                event.ignore()
        else:
            # Accept the close event and close the application
            event.accept()

    def stop_thread(self):
        # Implement a method that stops the thread
        self.foo.fooSignal.emit(self.processes_tab.table.rowCount()-1, "Stopped")
        self.processes_tab.save_data()