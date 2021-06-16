import ast

from de_alias_code import de_alias


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
    path = 'code.py'
    with open(path, encoding='utf-8') as f:
        source = f.read()

    source = de_alias(source)
    list_lines = source.split('\n')
    print('\n'.join([f'{i:<5}:    {line}' for i, line in enumerate(list_lines, start=1)]))

    tree = ast.parse(source)
    # print(ast.dump(tree, indent=4))
    parents = create_parents(tree)
    for node in ast.walk(tree):  # type: ast.AST
        if isinstance(node, ast.Name) and node.id == 'torch':
            list_nodes = find_grandparent(node, parents)

            result = []
            for cur_node in list_nodes:
                assert isinstance(cur_node, (ast.Name, ast.Attribute))
                result.append(cur_node.id if isinstance(cur_node, ast.Name) else cur_node.attr)
            print(node.lineno, '.'.join(result))
            # print(ast.dump(node, indent=4))


if __name__ == "__main__":
    main()
