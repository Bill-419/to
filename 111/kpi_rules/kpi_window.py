import sys
from PySide6.QtWidgets import QVBoxLayout, QWidget, QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from kpi_rules.generate_kpi_html import generate_kpi_window_html


class KpiWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("KPI 指标窗口")
        self.setGeometry(100, 100, 800, 600)

        # 创建布局
        layout = QVBoxLayout(self)

        # 生成HTML内容
        rules_string = """1、根据问题划分问题牵头领域，问题牵头领域牵头问题直至问题闭环（产品各领域版本PL认同）；
        2、根据问题单不过夜原则，测试当天会把非问题之外的问题单提给牵头领域，牵头领域在问题定界之前不走单；提单传递刚好卡点的话上一棒领域牵头；（大体原则24小时提单，如果上午10点半之前发出来的问题可以当天提，10点半后的第二天提，提单到对应指标责任组）
        3、结合总体原则2，如果某特定领域超过一天无法给出定位结论，问题单从牵头领域转交给定位领域（需要定位到单个LM团队问题的时候才可以走单），如果需要别的组配合超过一天没有响应或者无法解释关键点，可以通过复制问题单到对应组件；
        4、如果多个指标变化，挂靠别的指标的需要给出具体数据分析（不能只看报表传递），与对应组和测试达成一致，这种情况下测试提单只提到影响指标组件，不用每个指标提单，达不成一致，各领域提单；领域内达不成一致，按指标对应组分别提单；后续分析发现一致性问题，且达成一致，合并问题单跟踪；（领域接口人和PPO要在领域内开工会对齐原则）
        5、其他规则外问题处理原则由专题组及时例会组织制定，专题组达不成一致，由专题组长确认；
        6、不定期组织KPI运作改进会议，优秀经验及时分享，针对不足和问题讨论改进点（涉及维测过大导致流控等阻塞定位等）未及时改进版本层面通过对应领域。"""

        html_content = generate_kpi_window_html(rules_string)

        # 创建QWebEngineView并设置HTML内容
        self.browser = QWebEngineView()
        self.browser.setHtml(html_content)

        # 添加浏览器到布局
        layout.addWidget(self.browser)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KpiWindow()
    window.show()
    sys.exit(app.exec())
