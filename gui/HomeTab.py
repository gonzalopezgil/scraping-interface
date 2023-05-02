from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QStyle, QStyleOption
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt

class HomeTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.settings_tab_layout = QVBoxLayout(self)

        # Add a QLabel for the title
        self.title_label = QLabel("Scraping Interface", self)
        self.title_label.setStyleSheet("font-size: 32px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.settings_tab_layout.addWidget(self.title_label)

        # Add a QLineEdit for the search/URL input
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Search or write URL")
        self.search_input.setMinimumWidth(600)
        font = self.search_input.font()
        font.setPointSize(25)
        self.search_input.setFont(font)
        self.settings_tab_layout.addWidget(self.search_input, alignment=Qt.AlignCenter)

        self.setStyleSheet("""
            HomeTab {
                background-image: url('background.jpg');
                background-repeat: no-repeat;
                background-position: center;
            }
        """)

    def paintEvent(self, event):
        option = QStyleOption()
        option.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, option, painter, self)
