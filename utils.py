import json
import os
import zipfile
import shutil
from typing import Any, Tuple
from collections.abc import Iterator

import printer


def save_json(path: str, data: Any) -> None:
    with open(path, 'w+', encoding='utf8') as f:
        f.write(json.dumps(data, indent=4))


def open_json(path: str) -> Any:
    with open(path, encoding='utf8') as f:
        return json.load(f)


def get_all_files(path: str) -> list[str]:
    result = []
    for root, dirs, files in os.walk(path):
        for filename in files:
            file_path = os.path.join(root, filename)
            result.append(file_path)
    return result


def iterate_zip_file(path: str) -> Iterator[Tuple[str, str]]:
    """
    解析 path 下面的所有 zip 文件（不会递归），每个文件进行解压后，把里面的文件挨个儿 yield 出来
    :param path:
    :return:
    """
    tmp_path = 'tmp'
    if os.path.exists(tmp_path):
        shutil.rmtree(tmp_path)
    os.makedirs(tmp_path)

    zip_files_paths = [(f, os.path.join(path, f)) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith('.zip')]
    print(len(zip_files_paths))
    for i, (zip_name, zip_file_path) in enumerate(zip_files_paths):
        # 清空之前的 zip 文件
        print('CLEANING')
        shutil.rmtree(tmp_path)
        os.makedirs(tmp_path)

        # 解压
        print(f'UNZIPPING {i}th file: {zip_file_path}')
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as f:
                f.extractall(tmp_path)
        except UnicodeEncodeError as e:  # https://stackoverflow.com/questions/41019624/python-zipfile-module-cant-extract-filenames-with-chinese-characters
            printer.warn('extractall', zip_file_path, e)
            continue

        files_paths = get_all_files(tmp_path)  # 获取所有文件

        for file_path in files_paths:
            yield zip_name, file_path

    shutil.rmtree(tmp_path)
