from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from PyQt5.QtGui import QIcon
from utils.manager.password_manager import create_key
import sys
import io
from static import icon_path
from PyQt5.QtCore import QTranslator, QLocale
import os

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

    translator = QTranslator(app)
    # Get the absolute path to the translation file
    translation_file = os.path.abspath("translations/translations.qm")
    print(f"Translation file: {translation_file}")

    if translator.load(QLocale("es_ES"), translation_file):  # Specify the desired target locale
        app.installTranslator(translator)

    app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()
    window.setMinimumSize(650, 850)
    window.show()
    app.exec_()
