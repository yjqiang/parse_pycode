"""
在 code 中，可能会有人使用
class A:
    def function0(self):
        "注释"

    def function1(self):
        return 0

这样移除注释的时候，会导致生成的结果错误
"""
from typing import Tuple
import ast
import re


def is_code_ok(code: list[str]) -> Tuple[bool, str]:
    """
    是否可被解析
    :param code:
    :return:
    """
    source = '\n'.join(code)
    try:
        ast.parse(source)
    except Exception as e:
        return False, str(e)
    return True, ''


def fix_code(data: dict) -> Tuple[bool, list[str]]:
    code: list[str] = data['code']
    result, error = is_code_ok(code)
    if result:
        return True, code

    result = re.search(r'expected an indented block \(<unknown>, line (\d+)\)', error)
    if result:
        index = int(result.group(1))
        for try_index in range(max(1, index-4), min(len(code) + 1, index+1)):
            tmp_code = code.copy()
            indent_count = 0  # 上一行的 indent
            for i in tmp_code[try_index-1]:
                if i == ' ':
                    indent_count += 1
                else:
                    break
            tmp_code.insert(try_index, f'{" " * (indent_count+4)}pass')  # 下一行比上一行多 4

            result, error = is_code_ok(tmp_code)
            if result:
                print(f'FIXED {data["data_id"]=}')
                return True, tmp_code

    return False, []
