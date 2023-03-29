from PyQt5.QtCore import QObject, pyqtSignal, QVariant

class SignalManager(QObject):
    fooSignal = pyqtSignal(int, QVariant, QVariant)