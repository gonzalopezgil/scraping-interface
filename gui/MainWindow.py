from PyQt5.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QFileDialog, QTableWidgetItem
from gui.BrowserTab import BrowserTab
from gui.ProcessesTab import ProcessesTab
from gui.SettingsTab import SettingsTab
from scrapers.ScrapyScraper import ScrapyScraper
from scrapers.ScrapySeleniumScraper import ScrapySeleniumScraper
import threading
from utils.SignalManager import SignalManager
from utils.ProcessManager import ProcessManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scraping Interface")
        self.resize(1800, 1000)

        # Create a QTabWidget to hold the tabs
        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)

        self.process_manager = ProcessManager()
        
        # Create the tabs
        self.browser_tab = BrowserTab(self, self.process_manager)
        self.processes_tab = ProcessesTab(self)
        self.settings_tab = SettingsTab(self)

        self.signal_manager = SignalManager()
        self.signal_manager.process_signal.connect(self.processes_tab.update_status)
        self.signal_manager.pagination_signal.connect(self.browser_tab.browser.page().on_pagination_button_clicked)

        self.thread = None
        self.file_name = None
        self.file_entered = threading.Event()

        self.browser_tab.download_button.clicked.connect(lambda: self.start_thread(self.browser_tab.browser.url().toString(), self.browser_tab.get_column_titles(), self.signal_manager))
        self.browser_tab.preview_button.clicked.connect(lambda: self.preview_scrape(self.browser_tab.browser.url().toString(), self.browser_tab.get_column_titles()))
        self.browser_tab.pagination_button.clicked.connect(self.on_pagination_button_clicked)

        # Add the tabs to the tab widget
        self.tabs.addTab(self.browser_tab, "Browser")
        self.tabs.addTab(self.processes_tab, "Processes")
        self.tabs.addTab(self.settings_tab, "Settings")
    
    def on_pagination_button_clicked(self):
        self.signal_manager.pagination_signal.emit()

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

    def start_thread(self, url, column_titles, signal_manager):
        self.processes_tab.add_row(self.browser_tab.browser.url().toString(), "", self.browser_tab.get_column_titles())
        row = self.processes_tab.table.rowCount()-1
        file_name = self.enter_file_name()
        if file_name:
            self.thread = threading.Thread(target=self.thread_function, args=(url, column_titles, file_name, signal_manager, row), daemon=True)
            self.thread.start()
        else:
            signal_manager.process_signal.emit(row, "Stopped", "")

    def thread_function(self, url, column_titles, file_name, signal_manager, row):
        self.tabs.setCurrentIndex(1)

        scraper = ScrapySeleniumScraper()
        scraper.scrape(url, column_titles, self.process_manager.get_all_first_texts(), self.process_manager.get_all_xpaths(), file_name, signal_manager, row)

    def preview_scrape(self, url, column_titles):
        scraper = ScrapyScraper()
        items = scraper.preview_scrape(url, column_titles, self.process_manager.get_all_first_texts(), self.process_manager.get_all_xpaths())
        if items is None or len(items) == 0:
            self.show_no_preview_results()
        else:
            self.browser_tab.set_table_data(items)

    def show_no_preview_results(self):
        QMessageBox.warning(self, "Warning", "No preview results to show", QMessageBox.Ok)

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
            self.signal_manager.process_signal.emit(self.processes_tab.table.rowCount()-1, "Stopped", "")
            self.processes_tab.save_data()