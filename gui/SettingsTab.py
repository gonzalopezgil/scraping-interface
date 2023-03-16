from PyQt5.QtWidgets import QWidget, QVBoxLayout

class SettingsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_tab_layout = QVBoxLayout(self)
        self.settings_tab_layout.addWidget(QWidget(self))