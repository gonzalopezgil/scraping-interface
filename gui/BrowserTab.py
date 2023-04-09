from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QScrollArea, QSizePolicy, QHeaderView, QInputDialog, QAbstractItemView
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer
import gui.JavaScriptStrings as jss
from utils.WebEnginePage import WebEnginePage

HOME_PAGE = "https://www.google.com"
URL_SEARCH_ENGINE = "https://www.google.com/search?q="
PLACEHOLDER_TEXT = "Search with Google or enter a URL"
COLUMN_COUNT = 10

class BrowserTab(QWidget):

    def __init__(self, parent=None, column_manager=None):
        super().__init__(parent)
        self.column_manager = column_manager
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
        #self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Set the table widget as the scroll area's widget
        self.scroll_area.setWidget(self.table_widget)

        # Allow users to edit column headers
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.horizontalHeader().setSectionsMovable(True)
        self.table_widget.horizontalHeader().sectionDoubleClicked.connect(self.change_column_header)

        # Create a Scraping bar with buttons
        self.scrape_bar = QWidget(self)
        self.scrape_bar_layout = QHBoxLayout(self.scrape_bar)

        # Add a button to show a preview of the scrape
        self.preview_button = QPushButton("Preview", self.scrape_widget)
        self.scrape_bar_layout.addWidget(self.preview_button)
        
        # Add a button to download the table contents as an Excel file
        self.download_button = QPushButton("Download Excel", self.scrape_widget)
        self.scrape_bar_layout.addWidget(self.download_button)

        self.scrape_widget_layout.addWidget(self.scrape_bar)

        page = WebEnginePage(self.browser, self.table_widget, self.column_manager)
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
                        for col in range(self.table_widget.columnCount())][:self.column_manager.get_column_count()]
        return column_titles

    def load_homepage(self):
        self.browser.load(QUrl(HOME_PAGE))

    def load_url(self):
        url = self.url_field.text()
        if " " in url or "." not in url:
            # If the URL contains spaces or doesn't contain a dot, search for it
            url = URL_SEARCH_ENGINE + url.replace(" ", "+")
        elif not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        self.browser.load(QUrl(url))

    def update_url_field(self, url):
        self.url_field.setText(url.toString())
        self.scrape_widget.setVisible(False)
        self.browser.page().runJavaScript(jss.UNHIGHLIGHT_TEXT_JS)
        self.column_manager.clear_columns()

    def toggle_scrape_widget(self):
        # Get the page
        page = self.browser.page()

        # Toggle the visibility of the scrape widget
        self.scrape_widget.setVisible(not self.scrape_widget.isVisible())

        # Disable links if the scrape widget is visible
        if self.scrape_widget.isVisible():
            self.table_widget.clear()
            self.table_widget.setRowCount(0)
            self.timer.singleShot(100, self.disable_links)
            page.runJavaScript(jss.HIGHLIGHT_TEXT_JS)
        # Enable links if the scrape widget is not visible
        else:
            self.timer.stop()
            page.runJavaScript(jss.ENABLE_LINKS_JS)
            page.runJavaScript(jss.UNHIGHLIGHT_TEXT_JS)
            self.column_manager.clear_columns()

    # Create a loop that continuously disables all links in the page
    def disable_links(self):
        self.browser.page().runJavaScript(jss.DISABLE_LINKS_JS)

    def change_column_header(self, index):
        current_header = self.table_widget.horizontalHeaderItem(index)
        new_header_text, ok = QInputDialog.getText(self, "Edit Column Header", "Enter new column header text:", QLineEdit.Normal, current_header.text() if current_header else "")
        if ok and new_header_text:
            new_header = QTableWidgetItem(new_header_text)
            self.table_widget.setHorizontalHeaderItem(index, new_header)