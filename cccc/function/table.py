from PySide6.QtWidgets import QMainWindow,QInputDialog, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QApplication,QColorDialog
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from function.menu_changed import MenuOperations
from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget, QCheckBox, \
    QDialog, QDialogButtonBox, QScrollArea, QHBoxLayout, QLabel
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt

class TableWidget(QWidget):
    def __init__(self, table=None, editable=False):
        super().__init__()
        self.editable = editable

        # if table is None:
        #     self.table = QTableWidget(2, 8)
        #     self.items = []
        #     for row in range(2):
        #         for col in range(8):
        #             item = QTableWidgetItem(f"Item {row + 1},{col + 1}")
        #             item.setBackground(QColor("#ffffff"))
        #             item.setForeground(QColor("#000000"))
        #             self.table.setItem(row, col, item)
        #             self.items.append(item)
        # else:
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

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    table_widget = TableWidget.create_table_widget(editable=True)
    main_window.setCentralWidget(table_widget)
    main_window.show()
    sys.exit(app.exec())