import ast


def parse_file(filename: str):
    with open(filename, encoding='utf-8') as f:
        return ast.parse(f.read(), filename=filename)


print(ast.dump(parse_file('code.py'), indent=4))
