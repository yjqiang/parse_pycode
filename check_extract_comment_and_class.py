from operator import itemgetter

import seaborn
import matplotlib.pyplot as plt
import pandas as pd

import utils


def main():
    path = 'data/extract_comment_and_class/result1'

    data_count = 0  # 多少数据

    # 统计注释的行数信息
    dict_comment_line_count = {}
    comment_line_count = 0

    # 统计代码的行数信息
    dict_code_line_count = {}
    code_line_count = 0

    for json_name, path in utils.iterate_json_file(path):
        datas = utils.open_json(path)
        data_count += len(datas)
        for data in datas:
            cur_comment_line_count = len(data['comment'])
            dict_comment_line_count[cur_comment_line_count] = dict_comment_line_count.get(cur_comment_line_count, 0) + 1
            comment_line_count += cur_comment_line_count

            cur_code_line_count = len(data['code'])
            dict_code_line_count[cur_code_line_count] = dict_code_line_count.get(cur_code_line_count, 0) + 1
            code_line_count += cur_code_line_count

    print(f'一共 {data_count} 条数据')
    print(f'comment 有 {comment_line_count} 行，平均 {comment_line_count/data_count} 行')
    print('前 20 多的 comment 统计为(注：格式为 (行数，次数)): ', sorted(dict_comment_line_count.items(), key=itemgetter(1), reverse=True)[:20])  # 根据 value 对 dict 进行 sort

    print(f'code 有 {code_line_count} 行，平均 {code_line_count/data_count} 行')
    print('前 20 多的 code 统计为(注：格式为 (行数，次数)): ', sorted(dict_code_line_count.items(), key=itemgetter(1), reverse=True)[:20])  # 根据 value 对 dict 进行 sort

    height = 1500
    width = 20
    fig, axes = plt.subplots(2, 1, figsize=(height, width))  # https://dev.to/thalesbruno/subplotting-with-matplotlib-and-seaborn-5ei8

    df = pd.DataFrame(dict_comment_line_count.items(), columns=['Line', 'Count'])
    seaborn.barplot(ax=axes[0], x='Line', y='Count', data=df)
    axes[0].set_title('COMMENT STATISTICS')

    df = pd.DataFrame(dict_code_line_count.items(), columns=['Line', 'Count'])
    seaborn.barplot(ax=axes[1], x='Line', y='Count', data=df)
    axes[0].set_title('CODE STATISTICS')

    plt.show()




if __name__ == '__main__':
    main()