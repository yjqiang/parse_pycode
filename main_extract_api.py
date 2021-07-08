from extract_used_api.main import check

if __name__ == '__main__':
    path = 'code.py'
    with open(path, encoding='utf-8') as f:
        source = f.read()
    check(source)
