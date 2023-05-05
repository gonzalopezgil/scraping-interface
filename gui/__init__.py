from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.password_manager import create_key
import sys
import io

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
    window = MainWindow()
    window.setMinimumSize(650, 500)
    window.show()
    app.exec_()
