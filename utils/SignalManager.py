from PyQt5.QtCore import QObject, pyqtSignal, QVariant

class SignalManager(QObject):
    process_signal = pyqtSignal(int, QVariant, QVariant)
    pagination_signal = pyqtSignal()
