def compare_dictionaries(original, modified):
    changes = []

    # 检查所有的键
    all_keys = set(original.keys()).union(modified.keys())

    for key in all_keys:
        original_value = original.get(key, None)
        modified_value = modified.get(key, None)

        if original_value != modified_value:
            if original_value is None:
                changes.append(f"键 '{key}' 新增了值 '{modified_value}'。")
            elif modified_value is None or modified_value == "":
                changes.append(f"键 '{key}' 被删除，原来的值是 '{original_value}'。")
            elif original_value == "":
                changes.append(f"键 '{key}' 添加了值 '{modified_value}'。")
            else:
                changes.append(f"键 '{key}' 从 '{original_value}' 变为 '{modified_value}'。")

    if changes:
        summary = "检测到以下变化：\n" + "\n".join(changes)
    else:
        summary = "未检测到任何变化。"

    return summary

# 示例字典数据
original_data = {
    'RN呈现点': '',
    'client_id': 'f2cdf2af-8a00-469c-8d06-9b7cc83bd004',
    'username': 'c50039964',
    '严重级别': '11222222222',
    '代码合入版本': '',
    '修改影响': '',
    '写作人信息': '',
    '标题': '',
    '标题详情': '',
    '根因分析': '222',
    '涉及制式': '',
    '涉及网元': '',
    '解决方案': '22',
    '问题单号': '1112',
    '问题描述': '122222222'
}

modified_data = {
    'RN呈现点': '',
    'client_id': 'f2cdf2af-8a00-469c-8d06-9b7cc83bd004',
    'username': 'c50039964',
    '严重级别': '11222222223',
    '代码合入版本': '',
    '修改影响': '',
    '写作人信息': '',
    '标题': '',
    '标题详情': '',
    '根因分析': '',
    '涉及制式': '',
    '涉及网元': '1',
    '解决方案': '22',
    '问题单号': '1112',
    '问题描述': '122222223'
}

# 调用函数并打印总结
summary = compare_dictionaries({}, modified_data)
print(summary)
