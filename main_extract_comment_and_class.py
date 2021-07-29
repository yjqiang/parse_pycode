import ast

import printer
import utils
from extract_used_api.de_alias_code import de_alias


def remove_doc(tree: ast.AST) -> ast.AST:
    """
    把注释都丢掉（单行的代码注释，ast 自己就丢了，这里仅处理那些例如函数等级别的注释）
    :param tree:
    :return:
    """
    for node in ast.walk(tree):
        if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef, ast.ClassDef, ast.Module)):
            continue
        if not (node.body and isinstance(node.body[0], ast.Expr)):
            continue
        first_line = node.body[0].value
        if isinstance(first_line, ast.Constant) and isinstance(first_line.value, str):
            del node.body[0]
    return tree


def remove_type_hint(tree: ast.AST) -> ast.AST:
    """
    把 type hint 丢掉
    :param tree:
    :return:
    """
    for node in ast.walk(tree):
        # https://docs.python.org/3/library/ast.html#ast.FunctionDef
        if isinstance(node, ast.FunctionDef):
            node.returns = None
            # remove all argument annotations
            if node.args.args:
                for arg in node.args.args:
                    arg.annotation = None
    return tree


def check_and_filter(node: ast.AST) -> bool:
    """
    看看是否符合规定
    :param node:
    :return:
    """
    if isinstance(node, ast.ClassDef) and ast.get_docstring(node) is not None:  # 过滤空注释:
        for base in node.bases:
            if ast.unparse(base) == 'torch.nn.Module':  # 继承了 torch.nn.Module
                return True
    return False


def main():
    max_len_per_file = 20000

    list_results = utils.open_json('data/download_repos/result/data.json')['list_results']
    dict_results = {zip_name: (username, repo_name) for username, repo_name, zip_name in list_results}

    data_id = 0
    cur_datas = []  # [{data_id: _, zip_name: _, username: _, repo_name: _, comment: [_, ...], code: [_, ...]}, ...]  # 按照换行进行切分 comment 和 code
    for zip_name, path in utils.iterate_zip_file('data/download_repos/result'):
        # if zip_name != 'code.zip':
        #     continue
        # 仅处理 python 文件
        if not path.endswith('.py'):
            continue

        with open(path, encoding='utf-8') as f:
            try:  # UnicodeDecodeError: 'utf-8' codec can't decode byte 0xb7 in position 18310: invalid start byte
                source = f.read()
            except UnicodeDecodeError as e:
                printer.warn('source=f.read()', path, e)
                continue
            try:  # 可能有些 python 2 代码等
                source = de_alias(source)  # 把 API 还原
                tree = ast.parse(source, type_comments=False)
            except Exception as e:
                printer.warn('at.parse(source)', path, e)
                continue

            for node in ast.walk(tree):  # type: ast.AST
                if check_and_filter(node):
                    comment = ast.get_docstring(node)
                    code = ast.unparse(remove_type_hint(remove_doc(node)))  # 把代码格式进行统一
                    print(f'{data_id=}, {zip_name=}, {path=}')
                    #
                    # if (data_id+1) % 1000 == 0 and data_id != 0:
                    #     # print('---', ast.unparse(node))
                    #     print(ast.dump(node, indent=4))

                    # 保存数据
                    cur_datas.append({
                        'data_id': data_id,
                        'zip_name': zip_name,
                        'username': dict_results[zip_name][0],
                        'repo_name': dict_results[zip_name][1],
                        'comment': comment.split('\n'),
                        'code': code.split('\n')
                    })
                    if (data_id+1) % max_len_per_file == 0 and data_id != 0:
                        utils.save_json(f'data/extract_comment_and_class/result0/data{int(data_id/max_len_per_file)}.json', cur_datas)
                        cur_datas = []

                    data_id += 1

    print(f'SUM {data_id}')


if __name__ == '__main__':
    main()
