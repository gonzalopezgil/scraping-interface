from PyQt5.QtWidgets import QWidget, QVBoxLayout

class ProcessesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.processes_tab_layout = QVBoxLayout(self)
        self.processes_tab_layout.addWidget(QWidget(self))