def generate_html(record):
    """
    生成可编辑且包含保存和刷新按钮的显示记录详细信息的 HTML 内容。

    :param record: 字典，包含记录的详细信息
    :return: 字符串，包含 HTML 内容
    """
    title = record.get('标题', '未定义标题')
    title_detail = record.get('标题详情', '').replace('\n', '<br>').replace(' ', '&nbsp;')
    code_version = record.get('代码合入版本', '')
    rn_location = record.get('RN呈现局点', '')
    writer_info = record.get('写作人信息', '')

    issue_number = record.get('问题单号', '')
    issue_description = record.get('问题描述', '')
    severity_level = record.get('严重级别', '')
    root_cause_analysis = record.get('根因分析', '')
    solution = record.get('解决方案', '')
    modification_impact = record.get('修改影响', '')
    involved_standard = record.get('涉及制式', '')
    involved_ne = record.get('涉及网元', '')

    html_content = f"""
    <html>
    <head>
        <title>记录详情</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: blue; font-family: '黑体', Arial, sans-serif; }}
            .title-detail {{ margin-top: 10px; margin-bottom: 20px; white-space: pre-wrap; }}
            .info-table, .main-table {{ width: 100%; margin-bottom: 20px; border-collapse: collapse; }}
            .info-table td, .main-table th, .main-table td {{ padding: 8px; text-align: left; border: 1px solid #ddd; }}
            .info-table .label, .main-table .label {{ background-color: #f0f0f0; white-space: nowrap; font-weight: bold; }}
            .info-table td {{ background-color: #f0f0f0; width: 30%; }}  /* 控制表格宽度占比 */
            .info-table td:last-child {{ width: 70%; background-color: white; white-space: pre-wrap; }}  /* 控制文本框换行 */
            .main-table th {{ background-color: #f4f4f4; width: 20%; }}  /* 控制表格宽度占比 */
            .main-table td {{ width: 80%; background-color: white; white-space: pre-wrap; overflow-y: auto; }}  /* 控制文本框换行 */
            [contenteditable="true"] {{ border: 1px solid #ddd; padding: 4px; }}
            .button-container {{ margin-top: 20px; }}
            button {{ padding: 10px 20px; font-size: 16px; margin-right: 10px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <h1 contenteditable="true">{title}</h1>
        <div class="title-detail" contenteditable="true">{title_detail}</div>

        <table class="info-table">
            <tr>
                <td class="label">代码合入版本</td>
                <td contenteditable="true">{code_version}</td>
            </tr>
            <tr>
                <td class="label">RN呈现局点</td>
                <td contenteditable="true">{rn_location}</td>
            </tr>
            <tr>
                <td class="label">写作人信息（姓名+工号）</td>
                <td contenteditable="true">{writer_info}</td>
            </tr>
        </table>

        <table class="main-table">
            <tr>
                <th class="label">问题单号</th>
                <td class="value" contenteditable="true">{issue_number}</td>
            </tr>
            <tr>
                <th class="label">问题描述</th>
                <td class="value" contenteditable="true">{issue_description}</td>
            </tr>
            <tr>
                <th class="label">严重级别</th>
                <td class="value" contenteditable="true">{severity_level}</td>
            </tr>
            <tr>
                <th class="label">根因分析</th>
                <td class="value" contenteditable="true">{root_cause_analysis}</td>
            </tr>
            <tr>
                <th class="label">解决方案</th>
                <td class="value" contenteditable="true">{solution}</td>
            </tr>
            <tr>
                <th class="label">修改影响</th>
                <td class="value" contenteditable="true">{modification_impact}</td>
            </tr>
            <tr>
                <th class="label">涉及制式</th>
                <td class="value" contenteditable="true">{involved_standard}</td>
            </tr>
            <tr>
                <th class="label">涉及网元</th>
                <td class="value" contenteditable="true">{involved_ne}</td>
            </tr>
        </table>

        <div class="button-container">
            <button onclick="saveContent()">保存</button>
            <button onclick="refreshContent()">刷新</button>
        </div>

        <script>
            function getContentData() {{
                return {{
                    '标题': document.querySelector('h1').innerText,
                    '标题详情': document.querySelector('.title-detail').innerText,
                    '代码合入版本': document.querySelector('.info-table tr:nth-child(1) td:nth-child(2)').innerText,
                    'RN呈现局点': document.querySelector('.info-table tr:nth-child(2) td:nth-child(2)').innerText,
                    '写作人信息': document.querySelector('.info-table tr:nth-child(3) td:nth-child(2)').innerText,
                    '问题单号': document.querySelector('.main-table tr:nth-child(1) td').innerText,
                    '问题描述': document.querySelector('.main-table tr:nth-child(2) td').innerText,
                    '严重级别': document.querySelector('.main-table tr:nth-child(3) td').innerText,
                    '根因分析': document.querySelector('.main-table tr:nth-child(4) td').innerText,
                    '解决方案': document.querySelector('.main-table tr:nth-child(5) td').innerText,
                    '修改影响': document.querySelector('.main-table tr:nth-child(6) td').innerText,
                    '涉及制式': document.querySelector('.main-table tr:nth-child(7) td').innerText,
                    '涉及网元': document.querySelector('.main-table tr:nth-child(8) td').innerText
                }};
            }}

            function saveContent() {{
                const data = getContentData();
                window.pywebview.api.save_record(data).then(result => {{
                    if (result.status === 'success') {{
                        alert('保存成功！');
                    }} else {{
                        alert('保存失败：' + result.message);
                    }}
                }});
            }}

            function refreshContent() {{
                location.reload(); // 刷新页面内容
            }}
        </script>
    </body>
    </html>
    """
    return html_content
