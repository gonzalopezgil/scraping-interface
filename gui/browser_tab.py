from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidgetItem, QScrollArea, QSizePolicy, QHeaderView, QInputDialog, QMenu, QAction, QAbstractItemView, QMessageBox, QCheckBox
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer, pyqtSlot
import web.javascript_strings as jss
from utils.web_engine_page import WebEnginePage
from scrapers.scrapy_scraper import ScrapyScraper
import threading
from bs4 import BeautifulSoup
from utils.custom_table_widget import CustomTableWidget
from utils.template_manager import save_template, get_column_data_from_template

PLACEHOLDER_TEXT = "Search or enter a URL"
COLUMN_COUNT = 0
PAGINATION_WIDGET_WIDTH_PERCENTAGE = 1/3

class BrowserTab(QWidget):

    def __init__(self, parent=None, process_manager=None, signal_manager=None, settings=None):
        super().__init__(parent)
        self.process_manager = process_manager
        self.signal_manager = signal_manager
        self.settings = settings
        self.browser_tab_layout = QVBoxLayout(self)
        self.browser_tab_layout.addWidget(QWidget(self))

        # Create a browser window
        self.browser = QWebEngineView(self)

        # Create a widget for scraping
        self.scrape_widget = QWidget(self)
        self.scrape_widget_layout = QVBoxLayout(self.scrape_widget)
        self.horizontal_scrape_layout = QHBoxLayout()
        self.scrape_tables_layout = QVBoxLayout()
        self.scrape_widget.hide()

        # Widget to manage pagination
        self.pagination_widget = QWidget(self)
        self.pagination_layout = QVBoxLayout(self.pagination_widget)
        self.pagination_widget.hide()

        self.horizontal_scrape_layout.addWidget(self.pagination_widget)

        self.pagination_checkbox = QCheckBox("Pagination", self)
        self.pagination_layout.addWidget(self.pagination_checkbox)
        self.pagination_checkbox.clicked.connect(self.set_pagination)

        self.pagination_xpath_input = QLineEdit(self)
        self.pagination_xpath_input.setPlaceholderText("Click on the pagination button or enter an XPath")
        self.pagination_xpath_input.setEnabled(False)
        self.pagination_layout.addWidget(self.pagination_xpath_input)

        # Create a scroll area to hold the table widget
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scrape_tables_layout.addWidget(self.scroll_area)

        # Create a table widget to show scraped data
        self.table_widget = CustomTableWidget(self)
        self.table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table_widget.setColumnCount(COLUMN_COUNT)
        self.table_widget.horizontalHeader().customContextMenuRequested.connect(self.create_horizontal_header_context_menu)
        self.table_widget.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(lambda pos: self.create_table_context_menu(pos, self.table_widget))
        self.table_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Signal to update the table widget
        self.signal_manager.table_items_signal.connect(self.set_table_data)

        # Set the table widget as the scroll area's widget
        self.scroll_area.setWidget(self.table_widget)

        # Allow users to edit column headers
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.horizontalHeader().setSectionsMovable(True)
        self.table_widget.horizontalHeader().sectionDoubleClicked.connect(self.change_column_header)
        self.table_widget.horizontalHeader().sectionMoved.connect(self.move_column)

        # Create a second table to edit the xpath of each column
        self.table_xpath = CustomTableWidget(self)
        self.table_xpath.verticalHeader().setVisible(False)
        self.table_xpath.horizontalHeader().setVisible(False)
        self.table_xpath.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_xpath.setMaximumHeight(32)
        self.table_xpath.cellChanged.connect(self.handle_cell_changed)
        self.table_xpath.customContextMenuRequested.connect(lambda pos: self.create_table_context_menu(pos, self.table_xpath))
        self.table_xpath.setContextMenuPolicy(Qt.CustomContextMenu)        

        self.scrape_tables_layout.addWidget(self.table_xpath)

        # Create a Scraping bar with buttons
        self.scrape_bar = QWidget(self)
        self.scrape_bar_layout = QHBoxLayout(self.scrape_bar)

        # Add a button to select the pagination element
        self.pagination_button = QPushButton("Pagination", self.scrape_widget)
        self.scrape_bar_layout.addWidget(self.pagination_button)

        self.pagination_clicked = False

        # Add a button to save template
        self.save_template_button = QPushButton("Save Template", self.scrape_widget)
        self.scrape_bar_layout.addWidget(self.save_template_button)
        self.save_template_button.clicked.connect(self.save_current_template)
        
        # Add a button to download the table contents as an Excel file
        self.download_button = QPushButton("Download Excel", self.scrape_widget)
        self.scrape_bar_layout.addWidget(self.download_button)

        page = WebEnginePage(self.browser, self.table_widget, self.table_xpath, self.process_manager, self.pagination_xpath_input)
        self.browser.setPage(page)
        page.runJavaScript(jss.START_JS)
        # Connect the urlChanged signal to update the URL field
        self.browser.urlChanged.connect(self.update_url_field)

        # Create a URL bar with navigation buttons
        self.navigation_bar = QWidget(self)
        self.navigation_bar_layout = QHBoxLayout(self.navigation_bar)
        self.back_button = QPushButton("<", self.navigation_bar)
        self.back_button.clicked.connect(self.browser.back)
        self.navigation_bar_layout.addWidget(self.back_button)

        self.forward_button = QPushButton(">", self.navigation_bar)
        self.forward_button.clicked.connect(self.browser.forward)
        self.navigation_bar_layout.addWidget(self.forward_button)

        self.refresh_button = QPushButton("Refresh", self.navigation_bar)
        self.refresh_button.clicked.connect(self.browser.reload)
        self.navigation_bar_layout.addWidget(self.refresh_button)

        self.home_button = QPushButton("Home", self.navigation_bar)
        self.home_button.clicked.connect(self.load_homepage)
        self.navigation_bar_layout.addWidget(self.home_button)

        self.url_field = QLineEdit(self.navigation_bar)
        self.url_field.returnPressed.connect(self.load_url)
        self.navigation_bar_layout.addWidget(self.url_field)
        self.url_field.setPlaceholderText(PLACEHOLDER_TEXT)
        self.url_field.setClearButtonEnabled(True)

        self.browser_tab_layout.addWidget(self.navigation_bar, 0, Qt.AlignTop)

        self.load_homepage()
        self.browser_tab_layout.addWidget(self.browser, 1)

        # Create a button to toggle the scrape widget
        self.scrape_button = QPushButton("Scrape", self.navigation_bar)
        self.scrape_button.clicked.connect(self.toggle_scrape_widget)
        self.navigation_bar_layout.addWidget(self.scrape_button, 0, Qt.AlignRight)

        # Add the scrape widget at the bottom of the browser
        self.horizontal_scrape_layout.addLayout(self.scrape_tables_layout)
        self.scrape_widget_layout.addLayout(self.horizontal_scrape_layout)
        self.scrape_widget_layout.addWidget(self.scrape_bar)
        self.browser_tab_layout.addWidget(self.scrape_widget, 0)

        # Create a QTimer to check for new links every second
        self.timer = QTimer(self)

        self.browser.loadFinished.connect(lambda: self.browser.page().runJavaScript(jss.LOGIN_DETECTION_JS))

        self.pagination_button.clicked.connect(self.toggle_pagination)

        self.selected_template = None

    def set_pagination(self, state):
        self.select_pagination()
        if state == 1:
            self.pagination_xpath_input.setEnabled(True)
        else:
            self.pagination_xpath_input.setEnabled(False)

    def toggle_pagination(self):
        if self.pagination_widget.isVisible():
            self.pagination_widget.hide()
        else:
            self.pagination_widget.show()
            widget_width = self.scrape_widget.width()
            widget_width = int(widget_width * (1 / 3))

            self.pagination_widget.setFixedWidth(widget_width)
        
    def get_column_titles(self):
        column_titles = [self.table_widget.horizontalHeaderItem(col).text() 
                        if self.table_widget.horizontalHeaderItem(col) else str(self.process_manager.get_column(col).get_visual_index())
                        for col in range(self.table_widget.columnCount())][:self.process_manager.get_column_count()]
        return column_titles

    def load_homepage(self):
        self.browser.load(QUrl(self.settings["home_page"]))

    def save_current_template(self):
        if save_template(self.url_field.text(), self.process_manager, self.get_column_titles()):
            self.show_message("Template saved successfully")
        else:
            self.show_message("Error saving template")

    def show_message(self, message):
        msg = QMessageBox(self)
        msg.setWindowTitle("Information")
        msg.setText(message)
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)

        msg.exec_()

    def load_url(self):
        url = self.url_field.text()
        if " " in url or "." not in url:
            # If the URL contains spaces or doesn't contain a dot, search for it
            url = self.settings["search_engine"] + url.replace(" ", "+")
        elif not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        self.browser.load(QUrl(url))

    def update_url_field(self, url):
        self.url_field.setText(url.toString())
        self.scrape_widget.setVisible(False)
        self.pagination_widget.setVisible(False)
        self.pagination_checkbox.setChecked(False)
        self.pagination_xpath_input.setEnabled(False)
        self.browser.page().runJavaScript(jss.START_JS)
        self.browser.page().runJavaScript(jss.UNHIGHLIGHT_TEXT_JS)
        self.process_manager.clear_columns()
        self.pagination_clicked = False

    def toggle_scrape_widget(self):
        # Get the page
        page = self.browser.page()

        # Toggle the visibility of the scrape widget
        self.scrape_widget.setVisible(not self.scrape_widget.isVisible())

        # Disable links if the scrape widget is visible
        if self.scrape_widget.isVisible():
            self.table_widget.clear()
            self.table_xpath.clear()
            self.table_widget.setRowCount(0)
            self.table_xpath.setRowCount(0)
            self.table_widget.setColumnCount(COLUMN_COUNT)
            self.table_xpath.setColumnCount(COLUMN_COUNT)
            self.timer.singleShot(100, self.disable_links)
            page.runJavaScript(jss.HIGHLIGHT_TEXT_JS)
        # Enable links if the scrape widget is not visible
        else:
            self.timer.stop()
            page.runJavaScript(jss.DISABLE_PAGINATION_JS)
            page.runJavaScript(jss.ENABLE_LINKS_JS)
            page.runJavaScript(jss.UNHIGHLIGHT_TEXT_JS)
            self.process_manager.clear_columns()
            self.pagination_clicked = False
            self.pagination_checkbox.setChecked(False)
            self.pagination_widget.setVisible(False)
            self.pagination_xpath_input.setEnabled(False)

    # Create a loop that continuously disables all links in the page
    def disable_links(self):
        self.browser.page().runJavaScript(jss.DISABLE_LINKS_JS)

    def select_pagination(self):
        self.pagination_clicked = not self.pagination_clicked
        page = self.browser.page()
        if self.pagination_clicked:
            page.runJavaScript(jss.SELECT_PAGINATION_JS)
        else:
            page.runJavaScript(jss.DISABLE_PAGINATION_JS)

    def change_column_header(self, index):
        current_header = self.table_widget.horizontalHeaderItem(index)
        new_header_text, ok = QInputDialog.getText(self, "Edit Column Header", "Enter new column header text:", QLineEdit.Normal, current_header.text() if current_header else "")
        if ok and new_header_text:
            new_header = QTableWidgetItem(new_header_text)
            self.table_widget.setHorizontalHeaderItem(index, new_header)

    @pyqtSlot(dict)
    def set_table_data(self, items):
        for i, key in enumerate(items.keys()):
            for j, item in enumerate(items[key]):
                if self.table_widget.rowCount() < j+1:
                    self.table_widget.setRowCount(j+1)
                self.table_widget.setItem(j, i, QTableWidgetItem(item))
    
    def preview_scrape(self, html):
        html = self.clean_html(html)
    
        thread = threading.Thread(target=self.thread_preview_scrape, args=(self.browser.url().toString(), self.get_column_titles(), self.process_manager.get_all_xpaths(), html), daemon=True)
        thread.start()

    def thread_preview_scrape(self, url, column_titles, xpaths, html):
        scraper = ScrapyScraper()
        items = scraper.scrape(url, column_titles, xpaths, html, max_items=5)
        if items is not None and len(items) > 0:
            self.signal_manager.table_items_signal.emit(items)

    def handle_cell_changed(self, row, column):
        xpath = self.table_xpath.item(row, column).text()
        self.process_manager.get_column(column).set_xpath(xpath)
        self.paint_red_background(xpath)
        self.browser.page().toHtml(self.preview_scrape)

    def clean_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        # Remove the head tag
        if soup.head:
            soup.head.decompose()

        # Remove script tags (JavaScript)
        for script_tag in soup.find_all('script'):
            script_tag.decompose()

        # Remove style tags (CSS)
        for style_tag in soup.find_all('style'):
            style_tag.decompose()

        # Remove link tags (external CSS)
        for link_tag in soup.find_all('link', rel='stylesheet'):
            link_tag.decompose()

        # Remove iframe tags
        for iframe_tag in soup.find_all('iframe'):
            iframe_tag.decompose()

        # Remove img tags (images)
        for img_tag in soup.find_all('img'):
            img_tag.decompose()

        # Remove video tags
        for video_tag in soup.find_all('video'):
            video_tag.decompose()

        # Remove audio tags
        for audio_tag in soup.find_all('audio'):
            audio_tag.decompose()

        # Remove input tags (form elements)
        for input_tag in soup.find_all('input'):
            input_tag.decompose()

        return str(soup)
    
    def remove_red_background(self, xpath):
        js_code = f"var xpath = '{xpath}'; {jss.REMOVE_RED_BACKGROUND_JS}"
        self.browser.page().runJavaScript(js_code)

    def paint_red_background(self, xpath):
        js_code = f"var xpath = '{xpath}'; {jss.PAINT_RED_BACKGROUND_JS}"
        self.browser.page().runJavaScript(js_code)
    
    def remove_column(self, column):
        xpath = self.table_xpath.item(0, column).text()
        self.table_widget.removeColumn(column)
        self.table_xpath.removeColumn(column)
        self.process_manager.remove_column(column)
        self.remove_red_background(xpath)

    def create_horizontal_header_context_menu(self, pos):
        column = self.table_widget.horizontalHeader().logicalIndexAt(pos)
        menu = QMenu(self)
        remove_action = menu.addAction("Remove Column")
        remove_action.triggered.connect(lambda: self.remove_column(column))
        menu.exec_(self.table_widget.mapToGlobal(pos))

    def create_table_context_menu(self, pos, table):
        # Get the index of the cell at the position pos
        index = table.indexAt(pos)

        # Check if the index is valid
        if index.isValid():
            column = index.column()
            menu = QMenu(self)
            remove_action = QAction("Remove Column", self)
            remove_action.triggered.connect(lambda: self.remove_column(column))
            menu.addAction(remove_action)
            menu.exec_(table.viewport().mapToGlobal(pos))

    def move_column(self, logical_index, old_visual_index, new_visual_index):
        self.process_manager.move_column(old_visual_index, new_visual_index)

        self.table_xpath.horizontalHeader().blockSignals(True)  # Temporarily block signals to avoid infinite loop
        self.table_xpath.horizontalHeader().moveSection(old_visual_index, new_visual_index)
        self.table_xpath.horizontalHeader().blockSignals(False)  # Re-enable signals

    def load_template(self, template):
        # Open the scrape widget
        self.scrape_widget.show()

        # Browse to the URL
        self.browser.load(QUrl(template['url']))

        self.selected_template = template

        self.browser.loadFinished.connect(self.set_template)

    def set_template(self):
        self.scrape_widget.setVisible(False)
        self.toggle_scrape_widget()

        # Save all this information in the current process manager (including the pagination xpath if it exists)
        self.update_process_manager(self.selected_template)

        # Set column titles
        self.set_column_titles(get_column_data_from_template(self.selected_template, "column_title"))

        # Set the first texts in the first row of the table widget
        self.set_first_row_data(get_column_data_from_template(self.selected_template, "first_text"))

        # Set the xpaths in the xpath table
        self.set_xpaths(get_column_data_from_template(self.selected_template, "xpath"))

        self.browser.loadFinished.disconnect(self.set_template)

    def set_column_titles(self, column_titles):
        self.table_widget.setColumnCount(len(column_titles))
        self.table_xpath.setColumnCount(len(column_titles))
        for i, title in enumerate(column_titles):
            header_item = QTableWidgetItem(title)
            self.table_widget.setHorizontalHeaderItem(i, header_item)

    def set_first_row_data(self, first_row_data):
        self.table_widget.setRowCount(1)
        for i, data in enumerate(first_row_data):
            item = QTableWidgetItem(data)
            self.table_widget.setItem(0, i, item)

    def set_xpaths(self, xpaths):
        self.table_xpath.setRowCount(1)
        for i, xpath in enumerate(xpaths):
            item = QTableWidgetItem(xpath)
            self.table_xpath.setItem(0, i, item)

    def update_process_manager(self, template):
        self.process_manager.clear_columns()
        for i, (xpath, text) in enumerate(zip(get_column_data_from_template(template, "xpath"), get_column_data_from_template(template, "first_text"))):
            self.process_manager.create_column(xpath)
            self.process_manager.set_first_text(i, text)
        if 'pagination_xpath' in template and template['pagination_xpath'] is not None:
            self.process_manager.pagination_xpath(template['pagination_xpath'])

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.pagination_widget.isVisible():
            widget_width = self.scrape_widget.width()
            widget_width = int(widget_width * PAGINATION_WIDGET_WIDTH_PERCENTAGE)
            self.pagination_widget.setFixedWidth(widget_width)
