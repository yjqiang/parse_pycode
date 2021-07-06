import ast


def check(source: str) -> None:
    list_lines = source.split('\n')
    print('\n'.join([f'{i:<5}:    {line}' for i, line in enumerate(list_lines, start=1)]))

    tree = ast.parse(source, type_comments=True)
    for node in ast.walk(tree):  # type: ast.AST
        if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
            print(node.lineno, ast.get_docstring(node))
