from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSplitter
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
import sys

class CustomMainWindow(QMainWindow):
    def __init__(self, title, color, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        label = QLabel(f"这是{title}的内容", self)
        layout.addWidget(label)

        self.set_background_color(color)

    def set_background_color(self, color):
        palette = self.palette()
        palette.setColor(QPalette.Window, color)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

class ContainerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # 创建QSplitter用于分割显示区域
        splitter = QSplitter(Qt.Horizontal)

        # 创建多个QMainWindow实例，并将其内容嵌入到ContainerWidget中
        main_window1 = CustomMainWindow("窗口1", QColor(255, 228, 225))
        main_window2 = CustomMainWindow("窗口2", QColor(225, 255, 225))
        main_window3 = CustomMainWindow("窗口3", QColor(225, 225, 255))

        # 将每个QMainWindow的中央小部件添加到splitter中
        splitter.addWidget(main_window1.centralWidget())
        splitter.addWidget(main_window2.centralWidget())
        splitter.addWidget(main_window3.centralWidget())

        splitter.setSizes([200, 200, 200])  # 设置初始大小
        layout.addWidget(splitter)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("主窗口")
        self.setGeometry(100, 100, 800, 600)

        # 嵌入ContainerWidget
        container = ContainerWidget(self)
        self.setCentralWidget(container)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
