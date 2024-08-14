from PySide6.QtCore import QTimer
from PySide6.QtWebEngineWidgets import QWebEngineView

class HtmlManager:
    def __init__(self, html_tab_widget):
        self.html_tab_widget = html_tab_widget
        self.open_html_files = {}  # 存储打开的HTML文件，键是单号，值是标签页的索引
        self.closing_tab = False  # 标志位，防止递归关闭

        # 连接标签页关闭信号到自定义槽函数
        self.html_tab_widget.tabCloseRequested.connect(self.close_tab)

    def is_html_open(self, issue_number):
        """检查是否有与给定问题单号对应的页面打开"""
        return issue_number in self.open_html_files

    def reload_html(self, issue_number, new_html_content):
        if issue_number in self.open_html_files:
            index = self.open_html_files[issue_number]
            web_view = self.html_tab_widget.widget(index)
            # 使用QTimer稍微延迟HTML内容加载，避免一些渲染问题
            QTimer.singleShot(0, lambda: web_view.setHtml(new_html_content))

    def open_html(self, issue_number, html_content):
        print(f"Attempting to open HTML with issue_number: {issue_number}")
        if issue_number not in self.open_html_files:
            index = self.html_tab_widget.addTab(QWebEngineView(), issue_number)
            web_view = self.html_tab_widget.widget(index)
            web_view.setHtml(html_content)
            self.open_html_files[issue_number] = index
            self.html_tab_widget.setCurrentIndex(index)
            print(f"Opened new tab for issue_number: {issue_number} at index: {index}")
        else:
            index = self.open_html_files[issue_number]
            self.html_tab_widget.setCurrentIndex(index)
            print(f"Switched to existing tab for issue_number: {issue_number} at index: {index}")
        self.print_opened_html_list()

    def close_tab(self, index):
        if self.closing_tab:
            print("close_tab called, but closing_tab flag is set. Exiting.")
            return

        print(f"close_tab called with index: {index}")
        issue_number_to_close = None
        for issue_number, tab_index in list(self.open_html_files.items()):
            if tab_index == index:
                issue_number_to_close = issue_number
                break

        if issue_number_to_close:
            self.close_html(issue_number_to_close)

    def close_html(self, issue_number):
        print(f"close_html called with issue_number: {issue_number}")
        self.closing_tab = True
        if issue_number in self.open_html_files:
            index = self.open_html_files.pop(issue_number)
            self.html_tab_widget.removeTab(index)
            self._reindex_tabs()

            if self.html_tab_widget.count() > 0:
                if index - 1 >= 0:
                    self.html_tab_widget.setCurrentIndex(index - 1)
                elif index < self.html_tab_widget.count():
                    self.html_tab_widget.setCurrentIndex(index)
        self.closing_tab = False
        print("Exiting close_html")

    def handle_modified_issue_number(self, old_issue_number, new_issue_number, new_html_content):
        """
        修改问题单号后的处理逻辑：关闭旧单号对应的页面，打开新单号对应的新页面
        """
        # 关闭旧单号对应的页面
        print(f"Handling modified issue number from {old_issue_number} to {new_issue_number}")
        self.close_html(old_issue_number)

        # 打开新单号对应的页面
        self.open_html(new_issue_number, new_html_content)

    def get_opened_html_list(self):
        return list(self.open_html_files.keys())

    def print_opened_html_list(self):
        opened_list = self.get_opened_html_list()
        print("Currently opened HTML files:", opened_list)

    def _reindex_tabs(self):
        new_open_html_files = {}
        for index in range(self.html_tab_widget.count()):
            title = self.html_tab_widget.tabText(index)
            new_open_html_files[title] = index
        self.open_html_files = new_open_html_files
        self.print_opened_html_list()
