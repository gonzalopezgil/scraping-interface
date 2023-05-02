from PyQt5.QtWidgets import QApplication
from gui.MainWindow import MainWindow
from utils.PasswordManager import create_key

def main():

    # Password manager key
    create_key()

    # Run the application
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()