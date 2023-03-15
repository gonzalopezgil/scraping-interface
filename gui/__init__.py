from PyQt5.QtWidgets import QApplication
from gui.MainWindow import MainWindow

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()