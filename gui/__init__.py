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

def main():

    # Password manager key
    create_key()

    # Set 'utf-8' encoding
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception as e:
        print(f"Warning: Error setting the 'utf-8' encoding. {e}")

    # Run the application
    app = QApplication([])
    exit_code = RESTART_CODE

    while exit_code == RESTART_CODE:
        translator = QTranslator(app)

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
        translation_file = os.path.abspath(f"translations/translations_{locale}.qm")
        if translator.load(QLocale(locale), translation_file):  # Load the specified locale (if not found, don't translate)
            app.installTranslator(translator)

        app.setWindowIcon(QIcon(icon_path))
        window = MainWindow(app)
        window.setMinimumSize(650, 850)
        window.show()
        exit_code = app.exec_()
