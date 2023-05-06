from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QPushButton, QStyle, QStyleOption
from PyQt5.QtCore import Qt, QVariant, pyqtSlot
from PyQt5.QtGui import QPainter
import csv
from datetime import datetime
import os
from multiprocessing import Value
from static import background_path
#from utils.FileManager import get_file_path

#PROCESSES_FILE = get_file_path("processes.csv")
PROCESSES_FILE = "processes.csv"

class ProcessesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.processes_tab_layout = QVBoxLayout(self)
        self.table = QTableWidget(self)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(['Scraped Web', 'File Name', 'Scraped Items', 'Status', 'Date', 'Time', 'Action'])
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
        self.load_data()

        self.stop_variables = {}

        self.setStyleSheet(f"""
            ProcessesTab {{
                background-image: url({background_path});
                background-repeat: no-repeat;
                background-position: center;
            }}
        """)

    def create_open_file_button(self, file_name):
        open_file_button = QPushButton('Open')
        open_file_button.clicked.connect(lambda: self.open_file(file_name))
        return open_file_button
    
    def create_stop_button(self, row):
        stop_button = QPushButton('Stop')
        stop_button.clicked.connect(lambda: self.stop_process(row))
        return stop_button
        
    def load_data(self):
        try:
            with open(PROCESSES_FILE, newline='') as file:
                reader = csv.reader(file)
                data = list(reader)
                self.table.setRowCount(len(data))
                for row, item in enumerate(data):
                    self.table.setItem(row, 0, QTableWidgetItem(item[0]))
                    self.table.setItem(row, 1, QTableWidgetItem(item[1]))
                    self.table.setItem(row, 2, QTableWidgetItem(item[2]))
                    self.table.setItem(row, 3, QTableWidgetItem(item[3]))
                    self.table.setItem(row, 4, QTableWidgetItem(item[4]))
                    self.table.setItem(row, 5, QTableWidgetItem(item[5]))
                    if item[3] == "Finished":
                        self.table.setCellWidget(row, 6, self.create_open_file_button(item[1]))
                self.no_data_label.hide() # Hide label if data is found
                self.table.show() # Show table if data is found
        except FileNotFoundError:
            self.no_data_label.setText("No processes found") # Set label text if no data is found
            self.no_data_label.show() # Show label if no data is found
            self.table.hide() # Hide table if no data is found

    def add_row(self, scraped_web, file_name, column_titles):
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")
        self.table.setItem(row_count, 0, QTableWidgetItem(scraped_web))
        self.table.setItem(row_count, 1, QTableWidgetItem(file_name))
        self.table.setItem(row_count, 2, QTableWidgetItem(', '.join(column_titles)))
        self.table.setItem(row_count, 3, QTableWidgetItem("Running"))
        self.table.setItem(row_count, 4, QTableWidgetItem(date))
        self.table.setItem(row_count, 5, QTableWidgetItem(time))
        self.table.setCellWidget(row_count, 6, self.create_stop_button(row_count))
        self.table.show()
        self.no_data_label.hide()
        stop = Value('b', False)
        self.stop_variables[row_count] = stop
        return stop

    def get_table_data(self):
        table_data = []
        for row in range(self.table.rowCount()):
            row_data = [self.table.item(row, col).text()
                        for col in range(self.table.columnCount())
                        if self.table.item(row, col)]
            table_data.append(row_data)
        return table_data
    
    def save_data(self):
        with open(PROCESSES_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(self.get_table_data())

    def open_file(self, file_name):
        if os.name == 'nt':
            os.system(f'start {file_name}')
        elif os.name == 'posix':
            os.system(f"open '{file_name}'")
        else:
            print('Error: File is not opening due to unknown operating system')
        

    @pyqtSlot(int, QVariant, QVariant)
    def update_status(self, row, status, file_name):
        if status == "Finished":
            self.table.setCellWidget(row, 6, self.create_open_file_button(file_name))
        elif status == "Stopped" or status == "Error":
            self.table.setCellWidget(row, 6, None)
        self.table.setItem(row, 1, QTableWidgetItem(file_name))
        self.table.setItem(row, 3, QTableWidgetItem(status))
        self.save_data()

    def stop_process(self, row):
        self.stop_variables[row].value = True
        self.table.setItem(row, 3, QTableWidgetItem("Stopping..."))

    def paintEvent(self, _):
        option = QStyleOption()
        option.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, option, painter, self)
