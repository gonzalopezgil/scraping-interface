from PyQt5.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QFileDialog, QTableWidgetItem
from gui.BrowserTab import BrowserTab
from gui.ProcessesTab import ProcessesTab
from gui.SettingsTab import SettingsTab
from scrapers.ScrapyScraper import ScrapyScraper
import threading
from scrapy.crawler import CrawlerProcess
from utils.SignalManager import SignalManager
import scrapy.crawler as crawler
from multiprocessing import Process, Queue
from twisted.internet import reactor
import os

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
        self.file_name = None
        self.file_entered = threading.Event()

        self.browser_tab.download_button.clicked.connect(lambda: self.start_thread(self.browser_tab.browser.url().toString(), self.browser_tab.get_table_data(), self.foo))

        # Add the tabs to the tab widget
        self.tabs.addTab(self.browser_tab, "Browser")
        self.tabs.addTab(self.processes_tab, "Processes")
        self.tabs.addTab(self.settings_tab, "Settings")

    def enter_file_name(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Excel file", "", "Excel files (*.xlsx)")
        if filename:
            # Check if the file already exists
            i = 0
            coincidence = False
            while not coincidence and i < len(self.processes_tab.get_table_data()):
                row = self.processes_tab.get_table_data()[i]
                if filename == row[1]:
                    self.processes_tab.table.setItem(i, 1, QTableWidgetItem(""))
                    self.processes_tab.table.setItem(i, 3, QTableWidgetItem("Removed"))
                    self.processes_tab.table.removeCellWidget(i, 6)
                    coincidence = True
                i += 1
            return filename
        else:
            print("Error: no file name entered")
            return None

    def start_thread(self, url, data, foo):
        self.processes_tab.add_row(self.browser_tab.browser.url().toString(), "", self.browser_tab.get_table_data()[0])
        row = self.processes_tab.table.rowCount()-1
        #self.thread = threading.Thread(target=self.thread_function, args=(url, data, foo, row), daemon=True)
        #self.file_entered.clear()
        #self.thread.start()
        self.file_name = self.enter_file_name()
        #self.file_entered.set()
        self.thread_function(url, data, foo, row)

    def thread_function(self, url, data, obj, row):
        self.tabs.setCurrentIndex(1)

        scraper = ScrapyScraper()
        pid = os.fork()
        if pid == 0:
            scraper.scrape(url, data[0], data[1], data[2], self.file_name)
            os._exit(0)
        else:
            os.waitpid(pid, 0)
            if os.path.isfile(self.file_name):
                obj.fooSignal.emit(row, "Finished", self.file_name)
            else:
                obj.fooSignal.emit(row, "Error", "")

        #if df is None:
        #    obj.fooSignal.emit(row, "Error", "")
        #else:
        #    # Wait until the user enters a file name
        #    #if self.file_name is None:
        #    #    self.file_entered.wait()
        #    # Check again in case the user did not enter a file name
        #    if self.file_name is not None:
        #        self.save_file(df, self.file_name)
        #        obj.fooSignal.emit(row, "Finished", self.file_name)
        #        print("GUARDADO")
        #        self.file_name = None
        #    else:
        #        obj.fooSignal.emit(row, "Stopped", "")

    def save_file(self, dataframe, file_name):
        dataframe.to_excel(file_name)

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
        if self.thread.is_alive():
            # Implement a method that stops the thread
            self.foo.fooSignal.emit(self.processes_tab.table.rowCount()-1, "Stopped", "")
            self.processes_tab.save_data()