from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QScrollArea, QSizePolicy, QHeaderView, QInputDialog, QAbstractItemView
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer, pyqtSlot
import gui.JavaScriptStrings as jss
from utils.WebEnginePage import WebEnginePage
from scrapers.ScrapyScraper import ScrapyScraper
import threading
from bs4 import BeautifulSoup

PLACEHOLDER_TEXT = "Search or enter a URL"
COLUMN_COUNT = 5

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
        self.scrape_widget.hide()

        # Create a scroll area to hold the table widget
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scrape_widget_layout.addWidget(self.scroll_area)

        # Create a table widget to show scraped data
        self.table_widget = QTableWidget()
        self.table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table_widget.setColumnCount(COLUMN_COUNT)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.verticalHeader().setVisible(False)
        #self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Signal to update the table widget
        self.signal_manager.table_items_signal.connect(self.set_table_data)

        # Set the table widget as the scroll area's widget
        self.scroll_area.setWidget(self.table_widget)

        # Allow users to edit column headers
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.horizontalHeader().setSectionsMovable(True)
        self.table_widget.horizontalHeader().sectionDoubleClicked.connect(self.change_column_header)

        # Create a second table to edit the xpath of each column
        self.table_xpath = QTableWidget(0, COLUMN_COUNT)
        self.table_xpath.verticalHeader().setVisible(False)
        self.table_xpath.horizontalHeader().setVisible(False)
        self.table_xpath.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_xpath.setMaximumHeight(30)
        self.table_xpath.cellChanged.connect(self.handle_cell_changed)

        self.scrape_widget_layout.addWidget(self.table_xpath)

        # Create a Scraping bar with buttons
        self.scrape_bar = QWidget(self)
        self.scrape_bar_layout = QHBoxLayout(self.scrape_bar)

        # Add a button to select the pagination element
        self.pagination_button = QPushButton("Pagination", self.scrape_widget)
        self.pagination_button.clicked.connect(self.select_pagination)
        self.scrape_bar_layout.addWidget(self.pagination_button)

        self.pagination_clicked = False

        # Add a button to show a preview of the scrape
        self.preview_button = QPushButton("Preview", self.scrape_widget)
        self.scrape_bar_layout.addWidget(self.preview_button)
        
        # Add a button to download the table contents as an Excel file
        self.download_button = QPushButton("Download Excel", self.scrape_widget)
        self.scrape_bar_layout.addWidget(self.download_button)

        self.scrape_widget_layout.addWidget(self.scrape_bar)

        page = WebEnginePage(self.browser, self.table_widget, self.table_xpath, self.process_manager)
        self.browser.setPage(page)
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
        self.browser_tab_layout.addWidget(self.scrape_widget, 0)

        # Create a QTimer to check for new links every second
        self.timer = QTimer(self)

    def get_column_titles(self):
        column_titles = [self.table_widget.horizontalHeaderItem(col).text() 
                        if self.table_widget.horizontalHeaderItem(col) else str(col+1)
                        for col in range(self.table_widget.columnCount())][:self.process_manager.get_column_count()]
        return column_titles

    def load_homepage(self):
        self.browser.load(QUrl(self.settings["home_page"]))

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
            page.runJavaScript(jss.ENABLE_LINKS_JS)
            page.runJavaScript(jss.UNHIGHLIGHT_TEXT_JS)
            self.process_manager.clear_columns()
            self.pagination_clicked = False
            page.runJavaScript(jss.DISABLE_PAGINATION_JS)

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
        items = scraper.preview_scrape(url, column_titles, xpaths, html)
        if items is not None and len(items) > 0:
            self.signal_manager.table_items_signal.emit(items)

    def handle_cell_changed(self, row, column):
        self.process_manager.get_column(column).set_xpath(self.table_xpath.item(row, column).text())
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