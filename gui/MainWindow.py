from PyQt5.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QFileDialog, QTableWidgetItem
from gui.BrowserTab import BrowserTab
from gui.ProcessesTab import ProcessesTab
from gui.SettingsTab import SettingsTab
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
        self.signal_manager = SignalManager()

        self.settings = {
            "search_engine": "https://www.google.com/search?q=",
            "home_page": "https://www.google.com"
        }

        # Create the tabs
        self.settings_tab = SettingsTab(self, self.settings)
        self.browser_tab = BrowserTab(self, self.process_manager, self.signal_manager, self.settings)
        self.processes_tab = ProcessesTab(self)

        self.signal_manager.process_signal.connect(self.processes_tab.update_status)
        self.signal_manager.pagination_signal.connect(self.browser_tab.browser.page().on_pagination_button_clicked)

        self.thread = None
        self.file_name = None
        self.file_entered = threading.Event()

        self.browser_tab.download_button.clicked.connect(lambda: self.browser_tab.browser.page().toHtml(self.start_thread))
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

    def start_thread(self, html):
        url = self.browser_tab.browser.url().toString()
        column_titles = self.browser_tab.get_column_titles()
        process_manager = self.process_manager
        self.processes_tab.add_row(url, "", column_titles)
        row = self.processes_tab.table.rowCount()-1
        file_name = self.enter_file_name()
        if file_name:
            if self.process_manager.pagination_xpath:
                self.thread = threading.Thread(target=self.thread_function, args=(url, column_titles, file_name, row, process_manager), daemon=True)
            else:
                self.thread = threading.Thread(target=self.thread_function, args=(url, column_titles, file_name, row, process_manager, self.browser_tab.clean_html(html)), daemon=True)
            self.thread.start()
        else:
            self.signal_manager.process_signal.emit(row, "Stopped", "")

    def thread_function(self, url, column_titles, file_name, row, process_manager, html=None):
        self.tabs.setCurrentIndex(1)

        scraper = ScrapySeleniumScraper()
        scraper.scrape(url, column_titles, process_manager.get_all_first_texts(), process_manager.get_all_xpaths(), process_manager.pagination_xpath, file_name, self.signal_manager, row, html)

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