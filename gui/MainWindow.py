from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from gui.ProcessesTab import ProcessesTab
from gui.SettingsTab import SettingsTab

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
        # Connect the urlChanged signal to update the URL field
        self.browser.urlChanged.connect(self.update_url_field)

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

        # Create the tabs
        self.processes_tab = ProcessesTab(self)
        self.settings_tab = SettingsTab(self)

        # Add the tabs to the tab widget
        self.tabs.addTab(self.processes_tab, "Processes")
        self.tabs.addTab(self.settings_tab, "Settings")


        # Connect the "Browser" tab to open the Python browser
        self.tabs.currentChanged.connect(self.tab_changed)

        # Store the current URL when switching away from the "Browser" tab
        self.tabs.tabBarClicked.connect(self.store_current_url)

        # Create a widget for scraping
        self.scrape_widget = QWidget(self.browser_tab)
        self.scrape_widget_layout = QVBoxLayout(self.scrape_widget)
        self.scrape_widget.hide()

        # Create a button to toggle the scrape widget
        self.scrape_button = QPushButton("Scrape", self.navigation_bar)
        self.scrape_button.clicked.connect(self.toggle_scrape_widget)
        self.navigation_bar_layout.addWidget(self.scrape_button, 0, Qt.AlignRight)

        # Add a placeholder label to the scrape widget
        self.scrape_label = QLabel("Scrape Widget", self.scrape_widget)
        self.scrape_widget_layout.addWidget(self.scrape_label)

        # Add the scrape widget at the bottom of the browser
        self.browser_tab_layout.addWidget(self.scrape_widget, 0)

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

    def store_current_url(self, index):
        # Check if the clicked tab is not the "Browser" tab
        if index != self.tabs.indexOf(self.browser_tab):
            # Store the current URL of the browser
            self.stored_url = self.browser.url().toString()

    def tab_changed(self, index):
        if index == 0 and not self.browser.url().isEmpty():
            #self.browser_tab_layout.removeWidget(self.browser)
            #self.browser = QWebEngineView(self.browser_tab)
            #self.browser.load(QUrl(self.stored_url))
            #self.browser_tab_layout.addWidget(self.browser, 1)
            # Connect the urlChanged signal to update the URL field
            #self.browser.urlChanged.connect(self.update_url_field)
            pass

    def update_url_field(self, url):
        self.url_field.setText(url.toString())

    def toggle_scrape_widget(self):
        self.scrape_widget.setVisible(not self.scrape_widget.isVisible())