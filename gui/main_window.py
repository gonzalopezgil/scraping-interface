from PyQt5.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QFileDialog, QTableWidgetItem
from PyQt5.QtCore import QTimer, QUrl, pyqtSlot
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
import web.javascript_strings as jss
import copy
from utils.pyqt5_utils.progress_dialog import ProgressDialog
import os
import pandas as pd
import json
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()

        self.app = app

        self.setWindowTitle("Scraping Interface")
        self.setMinimumSize(1500, 850)
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
        self.signal_manager.browser_signal.connect(lambda: self.browser_tab.browser.page().toHtml(lambda html: self.start_thread(html)))
        self.signal_manager.tab_signal.connect(self.switch_to_process_tab)
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

        self.interaction = None
        self.stop = None
        self.current_page = 0
        self.row_count = 0
        self.actual_process_manager = None

        self.browser_tab.continue_button.clicked.connect(self.continue_process)
        self.browser_tab.cancel_button.clicked.connect(self.show_modal_dialog_to_cancel)

    def export_data(self, action):
        file_format = action.text().split(" ")[-1].lower()
        logger.info(f"Exporting data to {file_format}")

        self.browser_tab.browser.page().toHtml(lambda html: self.scrape(html, file_format))

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

    @pyqtSlot()
    def switch_to_process_tab(self):
        self.tabs.setCurrentIndex(2)
        self.dialog.close()

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
            logger.warning("Error: no file name entered")
            return None
        
    def count_rows(self, filename):
        if not filename or not os.path.exists(filename):
            logger.warning("File does not exist. No information found.")
            return None

        _, file_extension = os.path.splitext(filename)
        file_extension = file_extension.lower()

        if file_extension == ".csv":
            with open(filename, 'r') as f:
                return sum(1 for line in f) - 1  # subtract 1 to exclude header
        elif file_extension == ".xlsx":
            df = pd.read_excel(filename)
            return len(df)
        elif file_extension == ".json":
            with open(filename, 'r') as f:
                data = json.load(f)
            return len(data)
        elif file_extension == ".xml":
            tree = ET.parse(filename)
            root = tree.getroot()
            return len(root.findall('item'))
        else:
            logger.warning(f"Unsupported file format: {file_extension}")
            return None
        
    def change_page(self):
        self.browser_tab.process_manager.set_titles(self.browser_tab.get_column_titles())

        self.interaction = self.process_manager.interaction
        self.stop = self.process_manager.stop
        self.process_manager.interaction = None
        self.process_manager.stop = None
        process_manager = copy.deepcopy(self.browser_tab.process_manager)
                                           
        self.browser_tab.toggle_pagination()
        self.browser_tab.toggle_scrape_widget()
        js_code = f"var xpath = '{process_manager.pagination_xpath}'; {jss.CLICK_ELEMENT_JS}"
        self.browser_tab.browser.page().runJavaScript(js_code)

        if self.current_page < process_manager.max_pages:
            QTimer.singleShot(4000, lambda: self.browser_tab.set_process_manager(process_manager))
            self.process_manager = process_manager
            self.current_page += 1
        else:
            self.browser_tab.browser.load(QUrl(process_manager.url))
            self.process_manager = process_manager
            self.reset_process()
            QTimer.singleShot(4000, lambda: self.browser_tab.set_process_manager(process_manager, scrape=False))

    def require_user_interaction(self, file_name):
        count = self.count_rows(file_name)
        if not count or count <= self.row_count:
            self.dialog.close()
            self.browser_tab.enable_elements_layout(self.browser_tab.navigation_bar_layout, False)

            self.interaction = self.process_manager.interaction
            self.stop = self.process_manager.stop
            self.process_manager.interaction = None
            self.process_manager.stop = None
            self.actual_process_manager = copy.deepcopy(self.process_manager)

            self.browser_tab.pagination_widget.setVisible(True)
            self.browser_tab.scrape_widget.setVisible(True)
            self.browser_tab.toggle_pagination()
            self.browser_tab.toggle_scrape_widget()

            self.browser_tab.interaction_widget.show()
            
            QMessageBox.information(self, self.tr("Attention"), self.tr("No information found. Please interact with the browser to continue the process."))
        else:
            self.row_count = count
            self.change_page()

    def continue_process(self):
        self.browser_tab.interaction_widget.hide()
        self.process_manager = self.actual_process_manager
        self.actual_process_manager = None
        self.browser_tab.browser.page().toHtml(lambda html: self.start_thread(html))

    def cancel_process(self):
        self.row_count = 0
        self.browser_tab.interaction_widget.hide()
        process_manager = self.actual_process_manager
        self.actual_process_manager = None
        self.browser_tab.browser.load(QUrl(process_manager.url))
        self.process_manager = process_manager
        self.reset_process()
        self.browser_tab.enable_elements_layout(self.browser_tab.navigation_bar_layout, True)
        QTimer.singleShot(4000, lambda: self.browser_tab.set_process_manager(process_manager, scrape=False))

    def show_modal_dialog_to_cancel(self):
        self.dialog.show()
        QTimer.singleShot(0, self.cancel_process)

    def reset_process(self):
        self.stop = None
        self.interaction = None
        self.process_manager.stop = None
        self.process_manager.interaction = None
        self.process_manager.url = None
        self.process_manager.file_name = None
        self.process_manager.append = False
        self.process_manager.unique_id = None
        self.process_manager.max_pages = None

    def scrape(self, html, file_format):
        url = self.browser_tab.browser.url().toString()
        column_titles = self.browser_tab.get_column_titles()
        unique_id, stop, interaction = self.processes_tab.add_row(url, "", column_titles)
        append = self.browser_tab.pagination_widget.isVisible() and not self.browser_tab.automated_checkbox.isChecked()
        max_pages = self.browser_tab.max_pages_input.value()

        self.process_manager.append = append
        self.process_manager.unique_id = unique_id
        self.process_manager.stop = stop
        self.process_manager.interaction = interaction
        self.process_manager.url = url
        self.process_manager.max_pages = max_pages

        file_name = None
        if not self.process_manager.file_name:
            file_name = self.enter_file_name(file_format)
            if not file_name:
                return
            self.process_manager.file_name = file_name

        if append:
            self.dialog = ProgressDialog()
            self.dialog.show()
            QTimer.singleShot(0, lambda: self.start_thread(html))
        else:
            self.start_thread(html)

    def start_thread(self, html):
        file_name = self.process_manager.file_name
        append = self.process_manager.append
        url = self.browser_tab.browser.url().toString()
        column_titles = self.browser_tab.get_column_titles()
        unique_id = self.process_manager.unique_id
        process_manager = self.process_manager
        interaction = self.process_manager.interaction if self.process_manager.interaction else self.interaction
        stop = self.process_manager.stop if self.process_manager.stop else self.stop

        if file_name:
            if self.process_manager.pagination_xpath:
                if not self.browser_tab.automated_checkbox.isChecked():
                    max_pages = 1 # only download the current page
                else:    
                    max_pages = self.browser_tab.max_pages_input.value()
                    if not max_pages or max_pages == 0:
                        max_pages = None
                self.thread = threading.Thread(target=self.thread_function, args=(url, column_titles, file_name, unique_id, process_manager, self.signal_manager, interaction, html, stop, max_pages, append), daemon=True)
            else:
                if self.browser_tab.pagination_widget.isVisible():
                    self.process_manager.pagination_xpath = 'fake'
                self.thread = threading.Thread(target=self.thread_function, args=(url, column_titles, file_name, unique_id, process_manager, self.signal_manager, interaction, html, stop, 1, append), daemon=True)
            self.thread.start()
            if append:
                self.thread.join()
                self.require_user_interaction(file_name)
            else:
                self.tabs.setCurrentIndex(2)
                self.reset_process()
        else:
            self.signal_manager.process_signal.emit(unique_id, str(ProcessStatus.STOPPED.value), "")


    def thread_function(self, url, column_titles, file_name, row, process_manager, signal_manager, interaction, html=None, stop=None, max_pages=None, append=False):
        pagination_xpath = process_manager.pagination_xpath if max_pages and max_pages > 1 else None

        scraper = SeleniumScraper()
        scraper.before_scrape(url, column_titles, process_manager.get_all_first_texts(), process_manager.get_all_xpaths(), pagination_xpath, file_name, signal_manager, row, html, stop, interaction, max_pages, append)

    def show_no_preview_results(self):
        QMessageBox.warning(self, self.tr("Warning"), self.tr("No preview results to show"), QMessageBox.Ok)

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