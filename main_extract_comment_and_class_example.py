from extract_comment_and_class.main import check
from extract_used_api.de_alias_code import de_alias


if __name__ == '__main__':
    path = 'code.py'
    with open(path, encoding='utf-8') as f:
        source = f.read()
    source = de_alias(source)
    print(source)
    check(source)
