"""
过滤 main_extract_comment_and_class.py 的结果
"""
import utils


def all_english(string: str) -> bool:
    """
    https://stackoverflow.com/questions/27084617/detect-strings-with-non-english-characters-in-python
    https://docs.python.org/3/library/stdtypes.html#str.isascii
    :param string:
    :return:
    """
    return string.isascii()


def check(comment: list[str]) -> bool:
    for string in comment:
        if not all_english(string):
            return False
    return True


def main():
    orig_path = 'data/extract_comment_and_class/result0'
    new_path = 'data/extract_comment_and_class/result1'
    orig_count = 0
    new_count = 0
    for json_name, path in utils.iterate_json_file(orig_path):
        cur_datas = []
        datas = utils.open_json(path)
        orig_count += len(datas)
        for data in datas:
            if check(data['comment']):
                cur_datas.append(data)
            else:
                print(data['data_id'], data['comment'])

        new_count += len(cur_datas)
        utils.save_json(f'{new_path}/{json_name}', cur_datas)

    print(f'SUM {new_count}/{orig_count} = {new_count/orig_count:%}')


if __name__ == '__main__':
    main()
