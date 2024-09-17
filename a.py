from PySide6.QtCore import QUrl, QObject, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWidgets import QApplication
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)


class WebBridge(QObject):
    """用来连接 JavaScript 和 Python 的桥"""

    @Slot(str)
    def openUrl(self, url):
        logging.debug(f"URL clicked: {url}")
        QDesktopServices.openUrl(QUrl(url))


class MyWebView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.web_channel = QWebChannel()
        self.web_bridge = WebBridge()

        # 设置 webChannel，使得 HTML 中可以调用 Python 函数
        self.web_channel.registerObject("bridge", self.web_bridge)
        self.page().setWebChannel(self.web_channel)


def generate_html(record):
    """
    生成不可编辑且优化展示效果的记录详细信息的 HTML 内容。
    """
    title = record.get('标题', '未定义标题')
    title_detail = record.get('标题详情', '标签').replace('\n', '<br>').replace(' ', '&nbsp;')
    code_version = record.get('代码合入版本', '标签')
    rn_location = record.get('RN呈现点', '标签')
    writer_info = record.get('写作人信息', '标签')

    issue_number = record.get('问题单号', '标签')
    issue_description = record.get('问题描述', '标签')
    severity_level = record.get('严重级别', '标签')
    root_cause_analysis = record.get('根因分析', '标签')
    solution = record.get('解决方案', '标签')
    modification_impact = record.get('修改影响', '标签')
    involved_standard = record.get('涉及制式', '标签')

    # 假设 involved_ne 是一个 URL，例如 'www.baidu.com'
    involved_ne = record.get('涉及网元', 'www.baidu.com')
    involved_ne_link = f'<a href="{involved_ne}" target="_blank">{involved_ne}</a>'

    # 包含 JavaScript 代码，捕获点击事件并将其发送到 Qt
    html_content = f"""
    <html>
    <head>
        <title>记录详情</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ 
                color: black; 
                font-family: '黑体', Arial, sans-serif; 
                text-align: center; 
                font-size: 2em; 
                margin-bottom: 30px; 
            }}
            .title-detail {{
                margin-top: 10px; 
                margin-bottom: 30px;
                white-space: pre-wrap; 
                text-align: left; 
                padding: 10px;
                border: 1px solid #ddd;
                background-color: #f9f9f9;
            }}
            .info-table, .main-table {{ width: 100%; margin-bottom: 20px; border-collapse: collapse; }}
            .info-table td, .main-table th, .main-table td {{ padding: 12px; text-align: left; border: 1px solid #ddd; }}
            .info-table .label, .main-table .label {{ background-color: #f0f0f0; white-space: nowrap; font-weight: bold; }}
            .info-table td {{ background-color: #f9f9f9; width: 30%; }}
            .info-table td:last-child {{ width: 70%; background-color: white; white-space: pre-wrap; }}
            .main-table th {{ background-color: #f4f4f4; width: 20%; text-align: center; }}
            .main-table td {{ width: 80%; background-color: white; white-space: pre-wrap; text-align: left; }}
        </style>
        <script type="text/javascript" src="qrc:///qtwebchannel/qwebchannel.js"></script>
        <script type="text/javascript">
            function connectBridge() {{
                new QWebChannel(qt.webChannelTransport, function(channel) {{
                    bridge = channel.objects.bridge;

                    // 为所有超链接设置点击监听器
                    document.querySelectorAll('a').forEach(function(link) {{
                        link.addEventListener('click', function(event) {{
                            event.preventDefault();  // 阻止默认的打开行为
                            bridge.openUrl(link.href);  // 将 URL 发送给 Python
                        }});
                    }});
                }});
            }}
            window.onload = connectBridge;  // 当页面加载时连接 Qt
        </script>
    </head>
    <body>
        <h1>{title}</h1>
        <div class="title-detail">{title_detail}</div>

        <table class="info-table">
            <tr>
                <td class="label">代码合入版本</td>
                <td>{code_version}</td>
            </tr>
            <tr>
                <td class="label">RN呈现局点</td>
                <td>{rn_location}</td>
            </tr>
            <tr>
                <td class="label">写作人信息（姓名+工号）</td>
                <td>{writer_info}</td>
            </tr>
        </table>

        <table class="main-table">
            <tr>
                <th class="label">问题单号</th>
                <td class="value">{issue_number}</td>
            </tr>
            <tr>
                <th class="label">问题描述</th>
                <td class="value">{issue_description}</td>
            </tr>
            <tr>
                <th class="label">严重级别</th>
                <td class="value">{severity_level}</td>
            </tr>
            <tr>
                <th class="label">根因分析</th>
                <td class="value">{root_cause_analysis}</td>
            </tr>
            <tr>
                <th class="label">解决方案</th>
                <td class="value">{solution}</td>
            </tr>
            <tr>
                <th class="label">修改影响</th>
                <td class="value">{modification_impact}</td>
            </tr>
            <tr>
                <th class="label">涉及制式</th>
                <td class="value">{involved_standard}</td>
            </tr>
            <tr>
                <th class="label">涉及网元</th>
                <td class="value">{involved_ne_link}</td>
            </tr>
        </table>
    </body>
    </html>
    """
    return html_content


if __name__ == '__main__':
    app = QApplication([])

    view = MyWebView()
    record = {
        '标题': '记录示例',
        '标题详情': '这是一个示例记录的详情',
        '代码合入版本': 'v1.0',
        'RN呈现点': '点A',
        '写作人信息': '某某 - 工号12345',
        '问题单号': 'ISSUE-1234',
        '问题描述': '这是问题的描述',
        '严重级别': '高',
        '根因分析': '这是根因分析',
        '解决方案': '这是解决方案',
        '修改影响': '这是修改影响',
        '涉及制式': '5G',
        '涉及网元': 'www.baidu.com',  # 假设这里是一个URL
    }
    html_content = generate_html(record)
    view.setHtml(html_content)
    view.show()

    app.exec()
