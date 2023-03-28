from PyQt5.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QFileDialog, QTableWidgetItem
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
        self.file_name = None
        self.file_entered = threading.Event()

        self.browser_tab.download_button.clicked.connect(lambda: self.start_thread(self.browser_tab.browser.url().toString(), self.browser_tab.get_table_data(), self.foo))

        # Add the tabs to the tab widget
        self.tabs.addTab(self.browser_tab, "Browser")
        self.tabs.addTab(self.processes_tab, "Processes")
        self.tabs.addTab(self.settings_tab, "Settings")

    def enter_file_name(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Excel file", "", "Excel files (*.xlsx)")
        return filename

    def start_thread(self, url, data, foo):
        self.processes_tab.add_row(self.browser_tab.browser.url().toString(), "", self.browser_tab.get_table_data()[0])
        row = self.processes_tab.table.rowCount()-1
        self.thread = threading.Thread(target=self.thread_function, args=(url, data, foo, row), daemon=True)
        self.thread.start()
        self.file_name = self.enter_file_name()
        self.file_entered.set()
        self.processes_tab.table.setItem(row, 1, QTableWidgetItem(self.file_name))

    def thread_function(self, url, data, obj, row):
        self.tabs.setCurrentIndex(1)
        scraper = SeleniumScraper()
        df = scraper.scrape(url, data[0], data[2])
        print(self.file_name)
        if self.file_entered is None:
            self.file_entered.wait()
        self.save_file(df, self.file_name)
        obj.fooSignal.emit(row, "Finished")

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
            self.foo.fooSignal.emit(self.processes_tab.table.rowCount()-1, "Stopped")
            self.processes_tab.save_data()