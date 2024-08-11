# generate_kpi_html.py

def generate_kpi_window_html(rules_str):
    """
    生成一个HTML字符串，显示固定标题“KPI指标”和传入的规则。

    :param rules_str: 包含规则的字符串，用于在页面中显示。
    :return: 字符串，包含HTML内容。
    """
    # 将字符串按换行符分割成列表，每一项作为一条规则
    rules = rules_str.splitlines()

    html_content = f"""
    <html>
    <head>
        <title>KPI指标</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                margin: 0;
                padding: 0;
                height: 100vh;
                box-sizing: border-box;
                overflow: hidden;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            .container {{
                width: 90vw;
                height: 90vh;
                padding: 2vw;
                background-color: white;
                box-sizing: border-box;
                overflow-y: auto;
                border-radius: 1vw;
                box-shadow: 0 0 2vw rgba(0, 0, 0, 0.1);
            }}
            h1 {{
                color: #333;
                text-align: center;
                font-size: 3vw;
                margin-bottom: 2vw;
            }}
            .overview {{
                font-size: 1.5vw;
                margin-bottom: 2vw;
                font-weight: bold;
                color: #555;
                text-align: left;
            }}
            .rule-container {{
                text-align: left;
            }}
            .rule {{
                background-color: #e8f0fe;
                border-left: 0.5vw solid #1a73e8;
                padding: 1vw;
                margin-bottom: 1.5vw;
                font-size: 1.2vw;
                line-height: 1.5;
                border-radius: 0.5vw;
                box-sizing: border-box;
                white-space: pre-wrap;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>KPI指标</h1>
            <div class="overview">总体原则：</div>
            <div class="rule-container">
    """

    # 遍历规则并添加到HTML中
    for rule in rules:
        html_content += f'<div class="rule">{rule}</div>'

    html_content += """
            </div>
        </div>
    </body>
    </html>
    """

    return html_content
