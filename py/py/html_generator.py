def generate_html(record):
    """
    生成不可编辑且优化展示效果的记录详细信息的 HTML 内容。

    :param record: 字典，包含记录的详细信息
    :return: 字符串，包含 HTML 内容
    """
    title = record.get('标题', '未定义标题')
    title_detail = record.get('标题详情', '标签').replace('\n', '<br>').replace(' ', '&nbsp;')
    code_version = record.get('代码合入版本', '标签')
    rn_location = record.get('RN呈现局点', '标签')
    writer_info = record.get('写作人信息', '标签')

    issue_number = record.get('问题单号', '标签')
    issue_description = record.get('问题描述', '标签')
    severity_level = record.get('严重级别', '标签')
    root_cause_analysis = record.get('根因分析', '标签')
    solution = record.get('解决方案', '标签')
    modification_impact = record.get('修改影响', '标签')
    involved_standard = record.get('涉及制式', '标签')
    involved_ne = record.get('涉及网元', '标签')

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
                margin-bottom: 30px;  /* 增加标题与下面文字的间距 */
            }}
            .title-detail {{
                margin-top: 10px; 
                margin-bottom: 30px;  /* 增加文字与表格之间的间距 */
                white-space: pre-wrap; 
                text-align: left; 
                padding: 10px;
                border: 1px solid #ddd;
                background-color: #f9f9f9;
            }}
            .info-table, .main-table {{ width: 100%; margin-bottom: 20px; border-collapse: collapse; }}
            .info-table td, .main-table th, .main-table td {{ padding: 12px; text-align: left; border: 1px solid #ddd; }}
            .info-table .label, .main-table .label {{ background-color: #f0f0f0; white-space: nowrap; font-weight: bold; }}
            .info-table td {{ background-color: #f9f9f9; width: 30%; }}  /* 控制表格宽度占比 */
            .info-table td:last-child {{ width: 70%; background-color: white; white-space: pre-wrap; }}  /* 控制文本框换行 */
            .main-table th {{ background-color: #f4f4f4; width: 20%; text-align: center; }}  /* 控制表格宽度占比 */
            .main-table td {{ width: 80%; background-color: white; white-space: pre-wrap; text-align: left; }}  /* 控制文本框换行 */
        </style>
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
                <td class="value">{involved_ne}</td>
            </tr>
        </table>
    </body>
    </html>
    """
    return html_content
