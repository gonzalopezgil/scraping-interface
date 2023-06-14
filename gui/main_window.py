from PyQt5.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QFileDialog, QTableWidgetItem
from gui.browser_tab import BrowserTab
from gui.processes_tab import ProcessesTab
from gui.settings_tab import SettingsTab
from scrapers.selenium_scraper import SeleniumScraper
import threading
from utils.manager.signal_manager import SignalManager
from utils.manager.process_manager import ProcessManager
from gui.home_tab import HomeTab
from utils.manager.template_manager import load_template
from utils.manager.process_manager import ProcessStatus
import logging

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()

        self.app = app

        self.setWindowTitle("Scraping Interface")
        self.setMinimumSize(650, 850)
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
        self.home_tab = HomeTab(self)
        self.processes_tab = ProcessesTab(self)
        self.settings_tab = SettingsTab(self, self.settings, self.processes_tab, self, self.app)
        self.browser_tab = BrowserTab(self, self.process_manager, self.signal_manager, self.settings)

        self.signal_manager.process_signal.connect(self.processes_tab.update_status)
        self.signal_manager.pagination_signal.connect(self.browser_tab.browser.page().on_pagination_button_clicked)
        self.browser_tab.save_template_button.clicked.connect(self.home_tab.update_templates_list)
        self.settings_tab.clear_templates_button.clicked.connect(self.home_tab.update_templates_list)

        self.thread = None
        self.file_name = None
        self.file_entered = threading.Event()

        self.browser_tab.download_excel_action.triggered.connect(lambda: self.export_data(self.browser_tab.download_excel_action))
        self.browser_tab.download_csv_action.triggered.connect(lambda: self.export_data(self.browser_tab.download_csv_action))
        self.browser_tab.download_json_action.triggered.connect(lambda: self.export_data(self.browser_tab.download_json_action))
        self.browser_tab.download_xml_action.triggered.connect(lambda: self.export_data(self.browser_tab.download_xml_action))

        self.home_tab.search_input.returnPressed.connect(self.switch_to_browser_tab)

        # Add the tabs to the tab widget
        self.tabs.addTab(self.home_tab, self.tr("Home"))
        self.tabs.addTab(self.browser_tab, self.tr("Browser"))
        self.tabs.addTab(self.processes_tab, self.tr("Processes"))
        self.tabs.addTab(self.settings_tab, self.tr("Settings"))

        self.home_tab.template_clicked.connect(self.handle_template_click)

    def export_data(self, action):
        file_format = action.text().split(" ")[-1].lower()
        logger.info(f"Exporting data to {file_format}")

        self.browser_tab.browser.page().toHtml(lambda html: self.start_thread(html, file_format))

    def handle_template_click(self, template_id):
        # Change the tab to the BrowserTab
        self.tabs.setCurrentWidget(self.browser_tab)

        # Load the template data
        template = load_template(template_id)

        # Call the function to update the BrowserTab with the template data
        self.browser_tab.load_template(template)

    def switch_to_browser_tab(self):
        self.browser_tab.url_field.setText(self.home_tab.search_input.text())
        self.browser_tab.load_url()
        self.tabs.setCurrentIndex(1)

    def enter_file_name(self, file_format):
        file_extensions = {
            'excel': f"{self.tr('Excel files')} (*.xlsx)",
            'csv': f"{self.tr('CSV files')} (*.csv)",
            'json': f"{self.tr('JSON files')} (*.json)",
            'xml': f"{self.tr('XML files')} (*.xml)"
        }
        selected_filter = file_extensions.get(file_format, f"{self.tr('All files')} (*)")
        filename, selected_ext = QFileDialog.getSaveFileName(self, self.tr("Save File"), "", selected_filter)

        if filename:
            # Add the appropriate file extension if it's missing
            extension = selected_ext.split('(*')[1].split(')')[0]
            if not filename.endswith(extension):
                filename += extension

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
            logger.error("Error: no file name entered")
            return None

    def start_thread(self, html, file_format):
        url = self.browser_tab.browser.url().toString()
        column_titles = self.browser_tab.get_column_titles()
        process_manager = self.process_manager
        unique_id, stop, interaction = self.processes_tab.add_row(url, "", column_titles)
        file_name = self.enter_file_name(file_format)
        if file_name:
            if self.process_manager.pagination_xpath:
                max_pages = self.browser_tab.max_pages_input.value()
                if not max_pages or max_pages == 0:
                    max_pages = None
                self.thread = threading.Thread(target=self.thread_function, args=(url, column_titles, file_name, unique_id, process_manager, self.signal_manager, interaction, html, stop, max_pages), daemon=True)
            else:
                self.thread = threading.Thread(target=self.thread_function, args=(url, column_titles, file_name, unique_id, process_manager, self.signal_manager, interaction, html, stop, 1), daemon=True)
            self.thread.start()
        else:
            self.signal_manager.process_signal.emit(unique_id, str(ProcessStatus.STOPPED.value), "")

    def thread_function(self, url, column_titles, file_name, row, process_manager, signal_manager, interaction, html=None, stop=None, max_pages=None):
        self.tabs.setCurrentIndex(2)

        scraper = SeleniumScraper()
        scraper.before_scrape(url, column_titles, process_manager.get_all_first_texts(), process_manager.get_all_xpaths(), process_manager.pagination_xpath, file_name, signal_manager, row, html, stop, interaction, max_pages)

    def show_no_preview_results(self):
        QMessageBox.warning(self, self.tr("Warning"), self.tr("No preview results to show"), QMessageBox.Ok)

    def save_file(self, dataframe, file_name):
        dataframe.to_excel(file_name)

    def closeEvent(self, event):
        if self.thread and self.thread.is_alive():
            # Display a message box with a "Force Stop" button
            reply = QMessageBox.question(self, self.tr("Warning"), self.tr("The thread is still running. Do you want to force it to stop?"), QMessageBox.Yes | QMessageBox.No)
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
            self.signal_manager.process_signal.emit(self.processes_tab.table.rowCount()-1, str(ProcessStatus.STOPPED.value), "")
            self.processes_tab.save_data()