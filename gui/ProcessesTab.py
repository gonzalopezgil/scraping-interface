from PyQt5.QtWidgets import QWidget, QVBoxLayout

# Create a tab for the processes
class ProcessesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.processes_tab_layout = QVBoxLayout(self)
        self.processes_tab_layout.addWidget(QWidget(self))