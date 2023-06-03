from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QPushButton, QStyle, QStyleOption, QProgressBar
from PyQt5.QtCore import Qt, QVariant, pyqtSlot
from PyQt5.QtGui import QPainter
import csv
from datetime import datetime
import os
from multiprocessing import Value
from static import background_path
from utils.manager.file_manager import get_file_path
import sys
import threading
from utils.manager.process_manager import ProcessStatus
from plyer import notification
from static import icon_path
import logging

PROCESSES_FILE = get_file_path("processes.csv")
logger = logging.getLogger(__name__)

class ProcessesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.STATUS_STRINGS = {
            ProcessStatus.RUNNING: self.tr("Running"),
            ProcessStatus.STOPPING: self.tr("Stopping..."),
            ProcessStatus.FINISHED: self.tr("Finished"),
            ProcessStatus.ERROR: self.tr("Error"),
            ProcessStatus.REQUIRES_INTERACTION: self.tr("Requires interaction"),
            ProcessStatus.INTERACTING: self.tr("Interacting..."),
            ProcessStatus.STOPPED: self.tr("Stopped"),
            ProcessStatus.UNKNOWN: self.tr("Unknown")
        }

        self.processes_tab_layout = QVBoxLayout(self)
        self.table = QTableWidget(self)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([self.tr('Scraped Web'), self.tr('File Name'), self.tr('Scraped Items'), self.tr('Status'), self.tr('Date'), self.tr('Time'), self.tr('Action')])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch) # Set stretch factor for 'Scraped Web' column
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setStretchLastSection(False) # Disable stretching of last section
        self.processes_tab_layout.addWidget(self.table)
        self.no_data_label = QLabel(self) # Create label
        self.no_data_label.setAlignment(Qt.AlignCenter) # Center label
        self.processes_tab_layout.addWidget(self.no_data_label) # Add label to layout
        self.status_codes = [] # Stores status codes for each process
        self.load_data()

        self.stop_variables = {}
        self.interaction_variables = {}

        self.setStyleSheet(f"""
            ProcessesTab {{
                background-image: url({background_path});
                background-repeat: no-repeat;
                background-position: center;
            }}
        """)

    def create_open_file_button(self, file_name):
        open_file_button = QPushButton(self.tr('Open'))
        open_file_button.clicked.connect(lambda: self.open_file(file_name))
        return open_file_button
    
    def create_stop_button(self, row):
        stop_button = QPushButton(self.tr('Stop'))
        stop_button.clicked.connect(lambda: self.stop_process(row))
        return stop_button
    
    def create_interaction_button(self, row):
        interaction_button = QPushButton(self.tr('Interact'))
        interaction_button.clicked.connect(lambda: self.on_interaction(row))
        return interaction_button
    
    def create_resolved_button(self, row):
        resolved_button = QPushButton(self.tr('Resolved'))
        resolved_button.clicked.connect(lambda: self.on_resolved(row))
        return resolved_button
    
    def translate_status(self, status_code):
        status = ProcessStatus(status_code)
        return self.tr(self.STATUS_STRINGS.get(status, "Unknown"))
        
    def load_data(self):
        try:
            with open(PROCESSES_FILE, newline='') as file:
                reader = csv.reader(file)
                data = list(reader)
                self.table.setRowCount(len(data))
                for row, item in enumerate(data):
                    for col in range(len(item)):
                        if col == 3:
                            status = int(item[col]) if item[col] else ProcessStatus.ERROR.value
                            if status == ProcessStatus.FINISHED.value:
                                self.table.setCellWidget(row, 6, self.create_open_file_button(item[1]))
                            elif status in [ProcessStatus.RUNNING.value, ProcessStatus.STOPPING.value, ProcessStatus.REQUIRES_INTERACTION.value, ProcessStatus.INTERACTING.value]:
                                status = ProcessStatus.STOPPED.value
                            self.status_codes.append(status)
                            status_str = self.translate_status(status)
                            table_item = QTableWidgetItem(status_str)
                        else:
                            table_item = QTableWidgetItem(item[col])
                        table_item.setFlags(table_item.flags() & ~Qt.ItemIsEditable)  # Disable editing
                        self.table.setItem(row, col, table_item)
                
                self.save_data()

                self.no_data_label.hide() # Hide label if data is found
                self.table.show() # Show table if data is found
        except FileNotFoundError:
            self.no_data_label.setText(self.tr("No processes found")) # Set label text if no data is found
            self.no_data_label.show() # Show label if no data is found
            self.table.hide() # Hide table if no data is found
            self.table.setRowCount(0)

    def add_row(self, scraped_web, file_name, column_titles):
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        now = datetime.now()
        date = now.strftime("%d/%m/%Y")
        time = now.strftime("%H:%M:%S")
        
        status_code = ProcessStatus.RUNNING.value
        items = [scraped_web, file_name, ', '.join(column_titles), self.translate_status(status_code), date, time]
        self.status_codes.append(status_code)
        for col, text in enumerate(items):
            table_item = QTableWidgetItem(text)
            table_item.setFlags(table_item.flags() & ~Qt.ItemIsEditable)  # Disable editing
            self.table.setItem(row_count, col, table_item)
            
        self.table.setCellWidget(row_count, 6, self.create_stop_button(row_count))
        self.table.show()
        self.no_data_label.hide()
        stop = Value('b', False)
        self.stop_variables[row_count] = stop

        interaction = threading.Event()
        self.interaction_variables[row_count] = interaction

        return stop, interaction

    def get_table_data(self):
        table_data = []
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                if self.table.item(row, col):
                    if col == 3:
                        status_code = self.status_codes[row]
                        row_data.append(status_code)
                    else:
                        row_data.append(self.table.item(row, col).text())
                else:
                    row_data.append('')
            table_data.append(row_data)
        return table_data
    
    def save_data(self):
        try:
            with open(PROCESSES_FILE, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(self.get_table_data())
        except Exception as e:
            logger.error(f"Error saving processes: {e}")

    def open_file(self, file_name):
        if os.name == 'nt':
            os.system(f'start {file_name}')
            logger.info(f"Opening file '{file_name}'")
        elif os.name == 'posix':
            if sys.platform.startswith('darwin'):
                os.system(f"open '{file_name}'")
            else:
                os.system(f"xdg-open '{file_name}'")
            logger.info(f"Opening file '{file_name}'")
        else:
            logger.error("Error: File is not opening due to unknown operating system")

    def show_notification(self, title, message):
        try:
            notification.notify(
                title=title,
                message=message,
                app_icon=icon_path,
                timeout=10,
            )
            logger.info(f"Notification shown: {title} - {message}")
        except Exception:
            logger.error("Error showing notification")

    @pyqtSlot(int, QVariant, QVariant)
    def update_status(self, row, status, file_name):
        if "%" in status:
            progress = QProgressBar()
            progress.setValue(int(status.replace("%", ""))) # Remove '%' character
            self.table.setItem(row, 3, None)
            self.table.setCellWidget(row, 3, progress)

            status_code = ProcessStatus.RUNNING.value
        else:
            # Remove QProgressBar from the cell
            self.table.setCellWidget(row, 3, None)

            status_code = int(status)
            self.table.setItem(row, 3, QTableWidgetItem(self.translate_status(status_code)))
            if status_code == ProcessStatus.FINISHED.value:
                self.table.setCellWidget(row, 6, self.create_open_file_button(file_name))
                self.show_notification(self.tr("Process finished"), self.tr("A process has finished successfully"))
            elif status_code == ProcessStatus.STOPPED.value or status_code == ProcessStatus.ERROR.value:
                self.table.setCellWidget(row, 6, None)
            elif status_code == ProcessStatus.REQUIRES_INTERACTION.value:
                self.table.setCellWidget(row, 6, self.create_interaction_button(row))
                self.show_notification(self.tr("Interaction required"), self.tr("Please interact with the browser to continue the process"))
        self.status_codes[row] = status_code
        self.table.setItem(row, 1, QTableWidgetItem(file_name))
        self.save_data()

    def stop_process(self, row):
        self.stop_variables[row].value = True
        status_code = ProcessStatus.STOPPING.value
        self.table.setCellWidget(row, 3, None)
        self.table.setItem(row, 3, QTableWidgetItem(self.translate_status(status_code)))
        self.status_codes[row] = status_code
        self.table.setCellWidget(row, 6, None)

    def on_interaction(self, row):
        self.interaction_variables[row].set()
        status_code = ProcessStatus.INTERACTING.value
        self.table.setItem(row, 3, QTableWidgetItem(self.translate_status(status_code)))
        self.table.setCellWidget(row, 6, self.create_resolved_button(row))
        self.status_codes[row] = status_code

    def on_resolved(self, row):
        self.interaction_variables[row].set()
        status_code = ProcessStatus.RUNNING.value
        self.table.setItem(row, 3, QTableWidgetItem(self.translate_status(status_code)))
        self.table.setCellWidget(row, 6, self.create_stop_button(row))
        self.status_codes[row] = status_code

    def paintEvent(self, _):
        option = QStyleOption()
        option.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, option, painter, self)
