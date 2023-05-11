from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from PyQt5.QtGui import QIcon
from utils.password_manager import create_key
import sys
import io
from static import icon_path

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
    app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()
    window.setMinimumSize(650, 850)
    window.show()
    app.exec_()
