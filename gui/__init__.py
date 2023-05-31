from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from PyQt5.QtGui import QIcon
from utils.manager.password_manager import create_key
import sys
import io
from static import icon_path
from PyQt5.QtCore import QTranslator, QLocale
import os
import json
from . constants import SETTINGS_FILE, LANGUAGES, RESTART_CODE
import logging
from utils.manager.file_manager import get_file_path

def main():

    # Set up logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create a console handler to print logs in the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Create a file handler to write logs to a file
    file_handler = logging.FileHandler(get_file_path('application.log'))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Password manager key
    create_key()

    # Set 'utf-8' encoding
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception as e:
        logger.warning(f"Warning: Error setting the 'utf-8' encoding. {e}")

    # Run the application
    app = QApplication([])
    exit_code = RESTART_CODE
    translator = QTranslator(app)

    while exit_code == RESTART_CODE:
        app.removeTranslator(translator)

        # Load settings
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
        except FileNotFoundError:
            settings = {}

        # Translate the app
        if 'locale' not in settings:
            system_locale = QLocale.system()
            language = system_locale.languageToString(system_locale.language())
            if language in LANGUAGES:
                settings['locale'] = LANGUAGES[language]
            else:
                settings['locale'] = 'en'

        locale = settings.get('locale')
        if locale != 'en':
            translator = QTranslator(app)
            translation_file = os.path.abspath(f"translations/translations_{locale}.qm")
            if translator.load(QLocale(locale), translation_file):  # Load the specified locale (if not found, don't translate)
                app.installTranslator(translator)

        app.setWindowIcon(QIcon(icon_path))
        window = MainWindow(app)
        window.setMinimumSize(650, 850)
        window.show()
        exit_code = app.exec_()
