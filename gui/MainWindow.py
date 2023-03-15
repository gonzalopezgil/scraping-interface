from PyQt5.QtCore import QUrl, Qt, QEvent
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView

HOME_PAGE = "https://www.google.com"
URL_SEARCH_ENGINE = "https://www.google.com/search?q="
PLACEHOLDER_TEXT = "Search with Google or enter a URL"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scraping Interface")
        self.resize(1800, 1000)

        # Create a QTabWidget to hold the tabs
        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)

        # Create a tab for the browser
        self.browser_tab = QWidget(self.tabs)
        self.browser_tab_layout = QVBoxLayout(self.browser_tab)
        # Create a browser window
        self.browser = QWebEngineView(self.browser_tab)

        # Create a URL bar with navigation buttons
        self.navigation_bar = QWidget(self.browser_tab)
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
        self.tabs.addTab(self.browser_tab, "Browser")

        # Connect the urlChanged signal to update the URL field
        self.browser.urlChanged.connect(self.update_url_field)

        # Create a tab for the processes
        self.processes_tab = QWidget(self.tabs)
        self.processes_tab_layout = QVBoxLayout(self.processes_tab)
        self.processes_tab_layout.addWidget(QWidget(self.processes_tab))
        self.tabs.addTab(self.processes_tab, "Processes")

        # Create a tab for the settings
        self.settings_tab = QWidget(self.tabs)
        self.settings_tab_layout = QVBoxLayout(self.settings_tab)
        self.settings_tab_layout.addWidget(QWidget(self.settings_tab))
        self.tabs.addTab(self.settings_tab, "Settings")

        # Connect the "Browser" tab to open the Python browser
        self.tabs.currentChanged.connect(self.tab_changed)

    def load_homepage(self):
        self.browser.load(QUrl(HOME_PAGE))
        self.url_field.setText(HOME_PAGE)

    def load_url(self):
        url = self.url_field.text()
        if " " in url or "." not in url:
            # If the URL contains spaces or doesn't contain a dot, search for it
            search_query = URL_SEARCH_ENGINE + url.replace(" ", "+")
            self.browser.load(QUrl(search_query))
            self.url_field.setText(search_query)
        elif url.startswith("http://") or url.startswith("https://"):
            self.browser.load(QUrl(url))
            self.url_field.setText(url)
        else:
            url = "https://" + url
            self.browser.load(QUrl(url))
            self.url_field.setText(url)

    def tab_changed(self, index):
        if index == 0:
            self.browser_tab_layout.removeWidget(self.browser)
            self.browser = QWebEngineView(self.browser_tab)
            self.browser.load(QUrl(HOME_PAGE))
            self.browser_tab_layout.addWidget(self.browser, 1)

    def update_url_field(self, url):
        self.url_field.setText(url.toString())