from PySide6.QtWidgets import QTabWidget
from PySide6.QtWebEngineWidgets import QWebEngineView

class HtmlTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)

    def add_tab(self, title, html_content):
        web_view = QWebEngineView()
        web_view.setHtml(html_content)
        index = self.addTab(web_view, title)
        self.setCurrentIndex(index)
        return index
