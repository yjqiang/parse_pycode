"""
解析代码（注意是 json 文件），统计 api
"""
import ast

import utils
from extract_used_api.de_alias_code import de_alias
import main_fix_code


def create_parents(root: ast.AST) -> dict[ast.AST, ast.AST]:
    """
    原来的树只有父节点指向自节点，现在提供一个反查接口
    :param root:
    :return:
    """
    parents = {}
    for cur_node in ast.walk(root):
        for child in ast.iter_child_nodes(cur_node):
            parents[child] = cur_node
    return parents


def find_grandparent(node, parents: dict[ast.AST, ast.AST]) -> list[ast.AST]:
    """
    找到所有的父节点
    :param node:
    :param parents:
    :return:
    """
    parent = node
    result = [parent]
    while True:
        tmp = parents[parent]
        if not isinstance(tmp, ast.Attribute):
            return result
        parent = tmp
        result.append(parent)


def main():
    statistics = {}
    path = 'data/extract_comment_and_class/result1'
    orig_count = 0
    new_count = 0
    for json_name, path in utils.iterate_json_file(path):
        datas = utils.open_json(path)
        orig_count += len(datas)
        for data in datas:
            result, code = main_fix_code.fix_code(data)
            if not result:
                print(f'ERROR {data["data_id"]=}')
                continue

            new_count += 1
            source = '\n'.join(code)

            source = de_alias(source)

            tree = ast.parse(source)

            parents = create_parents(tree)
            for node in ast.walk(tree):  # type: ast.AST
                if isinstance(node, ast.Name) and node.id == 'torch':  # 查询嵌套 torch.xx.xx
                    list_nodes = find_grandparent(node, parents)

                    items = []
                    for cur_node in list_nodes:
                        assert isinstance(cur_node, (ast.Name, ast.Attribute))
                        items.append(cur_node.id if isinstance(cur_node, ast.Name) else cur_node.attr)
                    usage = '.'.join(items)
                    statistics[usage] = statistics.get(usage, 0) + 1

        print(new_count, orig_count, statistics)
    utils.save_json('data.json', {
        'statistics': statistics,
    })


if __name__ == "__main__":
    main()
