from PySide6.QtWidgets import QMainWindow,QInputDialog, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QApplication,QColorDialog
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from function.menu_base import MenuOperations

class TableWidget(QWidget):
    def __init__(self, table=None, editable=False):
        super().__init__()
        self.editable = editable  

        if table is None:
            self.table = QTableWidget(2, 8)
            self.items = []  
            for row in range(2):
                for col in range(8):
                    item = QTableWidgetItem(f"Item {row + 1},{col + 1}")
                    item.setBackground(QColor("#ffffff"))  
                    item.setForeground(QColor("#000000"))  
                    self.table.setItem(row, col, item)
                    self.items.append(item) 
        else:
            self.table = table

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        
        if self.editable:
            self.menu_operations = MenuOperations(self.table, self.editable)
            self.table.cellDoubleClicked.connect(self.menu_operations.on_cell_double_clicked)
            self.table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.table.customContextMenuRequested.connect(self.menu_operations.open_menu)

    def get_table(self):
        return self.table

    @staticmethod
    def create_table_widget(editable=False):
        return TableWidget(editable=editable)