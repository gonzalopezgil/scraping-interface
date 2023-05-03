from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFormLayout, 
    QRadioButton, QComboBox, QGroupBox, QSpacerItem, QSizePolicy, QMessageBox
)
from PyQt5.QtCore import Qt
import json
from utils.PasswordManager import clear_stored_passwords
from exceptions.file_exceptions import FileDeletionException
from utils.FileManager import get_file_path

SEARCH_ENGINES = {
    "Google": ["https://www.google.com/search?q=", "https://www.google.com"],
    "Bing": ["https://www.bing.com/search?q=", "https://www.bing.com"],
    "DuckDuckGo": ["https://duckduckgo.com/?q=", "https://duckduckgo.com/"]
}

SETTINGS_FILE = get_file_path("settings.json")

default_engine = next(iter(SEARCH_ENGINES.keys()))
default_settings = {
    "search_engine": SEARCH_ENGINES[default_engine][0], 
    "home_page": SEARCH_ENGINES[default_engine][1]
}

class SettingsTab(QWidget):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)

        self.settings = settings

        # Create the UI elements
        self.search_engine_radio = QRadioButton("Search Engine Home Page")
        self.custom_home_page_radio = QRadioButton("Custom Home Page")
        self.search_engine_combo = QComboBox(self)

        self.home_page_edit = QLineEdit(self)
        self.custom_home_page_radio.toggled.connect(self.home_page_edit.setEnabled)
        self.search_engine_radio.clicked.connect(self.save_settings)

        self.clear_passwords_button = QPushButton("Clear Stored Passwords", self)
        self.clear_passwords_button.clicked.connect(self.clear_passwords)

        try:
            with open(SETTINGS_FILE, "r") as f:
                loaded_json = json.load(f)

                if "search_engine" in loaded_json and "home_page" in loaded_json:
                    # Both "search_engine" and "home_page" keys exist in the JSON object
                    self.settings.update(loaded_json)
                    self.check_values()
                else:
                    self.settings = default_settings
                    self.check_values()
                    self.save_json()
        except FileNotFoundError:
            self.check_values()
            self.save_json()

        self.home_page_edit.setText(self.settings["home_page"])

        for engine, urls in SEARCH_ENGINES.items():
            self.search_engine_combo.addItem(engine, urls[0])
        self.search_engine_combo.setCurrentText(self.get_search_engine_name())

        self.search_engine_combo.currentIndexChanged.connect(self.save_settings)

        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_settings)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        home_page_group = QGroupBox("Home Page")
        home_page_layout = QVBoxLayout()
        home_page_layout.addWidget(self.search_engine_radio)
        home_page_layout.addWidget(self.custom_home_page_radio)

        edit_layout = QHBoxLayout()
        edit_layout.addWidget(self.home_page_edit)
        edit_layout.addWidget(save_button)

        button_layout = QVBoxLayout()
        button_layout.addLayout(home_page_layout)
        button_layout.addLayout(edit_layout)

        home_page_group.setLayout(button_layout)

        form_layout.addRow(home_page_group)
        form_layout.addRow(QLabel("Search Engine:"), self.search_engine_combo)

        password_manager_label = QLabel("Password Manager:")
        form_layout.addRow(password_manager_label, self.clear_passwords_button)

        spacer_item = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        form_layout.addItem(spacer_item)

        widget = QWidget()
        widget.setLayout(form_layout)

        # Set the maximum width of the widget to 600 pixels
        widget.setMaximumWidth(600)

        layout.addWidget(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

    def check_values(self):
        # Check if the search engine is in the SEARCH_ENGINES dictionary
        if self.settings["home_page"] and self.settings["home_page"] not in [engine[1][1] for engine in SEARCH_ENGINES.items()]:
            self.custom_home_page_radio.setChecked(True)
            self.home_page_edit.setEnabled(True)
        elif self.settings["search_engine"] in [engine[1][0] for engine in SEARCH_ENGINES.items()]:
            self.search_engine_radio.setChecked(True)
            self.home_page_edit.setEnabled(False)
        else:
            # Save the default search engine URL in the settings file
            search_engine = self.get_search_engine_name()
            self.settings["search_engine"] = SEARCH_ENGINES[search_engine][0]
            self.save_json()
            self.search_engine_radio.setChecked(True)
            self.home_page_edit.setEnabled(False)
        self.home_page_edit.setText(self.settings["home_page"])

    def get_search_engine_name(self):
        for i in range(self.search_engine_combo.count()):
            if self.settings["search_engine"] and self.settings["search_engine"].startswith(self.search_engine_combo.itemData(i)):
                return self.search_engine_combo.itemText(i)
            if self.settings["home_page"] and self.settings["home_page"] != "":
                for engine, value in SEARCH_ENGINES.items():
                    url = self.settings["home_page"]
                    if url in value[1]:
                        return engine
        return next(iter(SEARCH_ENGINES)) # Return the first search engine
    
    def save_json(self):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f)

    def save_settings(self):
        # Update the settings dictionary with the new values
        if self.custom_home_page_radio.isChecked():
            self.settings["home_page"] = self.home_page_edit.text()
            self.settings["search_engine"] = self.search_engine_combo.currentData()
        else:
            self.settings["search_engine"] = self.search_engine_combo.currentData()
            self.settings["home_page"] = self.get_home_page_url()

        # Save the settings to the file
        self.check_values()
        self.save_json()

        if not self.custom_home_page_radio.isChecked():
            search_engine = self.get_search_engine_name()
            self.settings["search_engine"] = SEARCH_ENGINES[search_engine][0]
            self.settings["home_page"] = SEARCH_ENGINES[search_engine][1]

        self.home_page_edit.clearFocus()

    def get_home_page_url(self):
        for engine, urls in SEARCH_ENGINES.items():
            if self.search_engine_radio.isChecked() and self.settings["search_engine"].startswith(urls[0]):
                return urls[1]
        return self.settings["home_page"]

    # Unused
    def reset_settings(self):
        # Reset the settings dictionary to the defaults
        self.settings = default_settings
        self.check_values()
        self.save_json()

        # Update the UI elements
        self.search_engine_combo.setCurrentText(self.get_search_engine_name())
        self.home_page_edit.setText(self.settings["home_page"])
        self.custom_home_page_radio.setChecked(self.settings["search_engine"] is None)
        self.search_engine_radio.setChecked(not self.custom_home_page_radio.isChecked())

    def clear_passwords(self):
        try:
            msg = self.show_clear_passwords_message()
            message = ""
            if clear_stored_passwords():
                message = "All stored credentials have been removed."
            else:
                message = "No credentials were found."
            msg.setText(message)
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
        except FileDeletionException as e:
            msg = self.show_clear_passwords_message()
            msg.setText(e)
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()

    def show_clear_passwords_message(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Clear Stored Passwords")
        msg.setStandardButtons(QMessageBox.Ok)
        return msg
