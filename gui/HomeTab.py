from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QStyle, QStyleOption, QHBoxLayout, QScrollArea, QPushButton
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
from utils.TemplateThumbnail import TemplateThumbnail
from utils.TemplateManager import list_templates

class HomeTab(QWidget):
    def __init__(self, parent=None, templates_per_page=8):
        super().__init__(parent)
        self.templates_per_page = templates_per_page
        self.current_page = 0

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

        #self.templates_label = QLabel("Saved templates", self)
        #self.templates_label.setAlignment(Qt.AlignCenter)
        #self.settings_tab_layout.addWidget(self.templates_label)

        self.templates_grid = QHBoxLayout()
        self.templates_scroll_area = QScrollArea()
        self.templates_scroll_area.setMaximumHeight(200)
        self.templates_scroll_area.setWidgetResizable(True)
        self.templates_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.templates_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.templates_scroll_area.setWidget(QWidget())
        self.templates_scroll_area.widget().setLayout(self.templates_grid)
        self.settings_tab_layout.addWidget(self.templates_scroll_area, alignment=Qt.AlignTop)
        self.templates_scroll_area.setStyleSheet("background-color: transparent;")

        self.setStyleSheet("""
            HomeTab {
                background-image: url('background.jpg');
                background-repeat: no-repeat;
                background-position: center;
            }
        """)

        # Add navigation buttons
        self.nav_buttons_layout = QHBoxLayout()
        self.previous_button = QPushButton("Previous")
        self.previous_button.clicked.connect(self.previous_page)
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_page)
        self.nav_buttons_layout.addWidget(self.previous_button)
        self.nav_buttons_layout.addWidget(self.next_button)
        self.settings_tab_layout.addLayout(self.nav_buttons_layout)

        self.templates = []
        self.previous_width = self.width()

        templates_list = list_templates()
        num_templates = len(templates_list)

        if not self.templates:
            for domain in templates_list:
                template_thumbnail = TemplateThumbnail(domain)
                self.templates.append(template_thumbnail)
                self.templates_grid.addWidget(template_thumbnail)

        self.start_index = self.current_page * self.templates_per_page
        self.end_index = min(self.start_index + self.templates_per_page, num_templates)

        self.change_page()

    def hide_templates(self):
        width = self.width()
        num_templates = len(self.templates)
        if width < 1750 and num_templates > 7:
            self.templates[7].hide()
        if width < 1500 and num_templates > 6:
            self.templates[6].hide()
        if width < 1200 and num_templates > 5:
            self.templates[5].hide()
        if width < 900 and num_templates > 4:
            self.templates[4].hide()

    def show_templates(self):
        width = self.width()
        num_templates = len(self.templates)
        if width >= 1750 and num_templates > 7:
            self.templates[7].show()
        if width >= 1500 and num_templates > 6:
            self.templates[6].show()
        if width >= 1200 and num_templates > 5:
            self.templates[5].show()
        if width >= 900 and num_templates > 4:
            self.templates[4].show()

    def update_templates(self):
        if self.width() > self.previous_width:
            self.show_templates()
        else:
            self.hide_templates()

    def change_page(self):
        num_shown_templates = self.get_num_shown_templates()
        start_index = self.current_page * num_shown_templates
        end_index = min(start_index + num_shown_templates, len(self.templates))

        for i, template in enumerate(self.templates):
            if start_index <= i < end_index:
                template.show()
            else:
                template.hide()

        # Update the navigation buttons
        self.previous_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(end_index < len(self.templates))

    def get_num_shown_templates(self):
        width = self.width()
        num_templates = len(self.templates)
        if width >= 1750 and num_templates > 7:
            return 8
        if width >= 1500 and num_templates > 6:
            return 7
        if width >= 1200 and num_templates > 5:
            return 6
        if width >= 900 and num_templates > 4:
            return 5
        return 4

    def next_page(self):
        self.current_page += 1
        self.change_page()

    def previous_page(self):
        self.current_page -= 1
        self.change_page()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_templates()
        self.previous_width = self.width()

    def paintEvent(self, event):
        option = QStyleOption()
        option.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, option, painter, self)
