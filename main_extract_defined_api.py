import torch

from extract_defined_api.main import get_submodules, locate, search_functions_and_classes, fullname

if __name__ == '__main__':
    # 爬取所有子模块
    modules = {torch}
    new_modules = modules  # 要干的活儿
    while True:
        if not new_modules:  # 结束
            break

        cur_modules_result = set()  # 本轮结果
        for parent_module in new_modules:
            try:
                str(parent_module)
            except Exception as e:
                print(f"!!!!!! {e}")
                continue
            try:
                submodules_names = get_submodules(parent_module)  # 找到当前模块下的子模块名字们
            except TypeError as e:
                print(f"!!!!!!1 {e} {parent_module=}")  # eg: <module 'torch.ops' from '_ops.py'>
                continue
            for submodule_name, sub_module in submodules_names:
                if submodule_name == 'torch':  # 有的文件里面 import torch  eg: E:\\Python\\Python39\\lib\\site-packages\\torch\\__init__.py
                    continue
                submodule_name = f'{parent_module.__name__}.{submodule_name}'

                if sub_module is None:
                    sub_module = locate(submodule_name)  # 转成可以直接使用的模块而不是 string

                # TODO: del
                if sub_module is None:
                    continue

                if sub_module.__name__.startswith('torch'):
                    cur_modules_result.add(sub_module)

        cur_modules_result -= modules  # 去重
        modules |= cur_modules_result
        new_modules = cur_modules_result

    print('-' * 20)

    # 爬取 api
    funcs = set()
    classes = set()
    datas = set()
    for module in modules:
        try:
            cur_funcs, cur_classes, cur_datas = search_functions_and_classes(module)
            funcs |= set(cur_funcs)
            classes |= set(cur_classes)
            datas |= set(cur_datas)
        except Exception as e:
            print(f"!!!!!!3 {e} {module.__name__=}")

    result0 = set()
    for name, value in funcs:
        print(f'funcs {name=}, {value}')
        result0.add(f'{value.__module__}.{name}')

    for name, value in classes:
        print(f'classes {name=}, {value}')
        result0.add(f'{value.__module__}.{name}')

    for name, value in datas:
        print(f'datas {name=}, {value}')
        result0.add(f'{value}.{name}')


    import json

    with open('data.json', encoding='utf-8') as f:
        orig = json.load(f)['result']
        result = set()
        for key, value in orig.items():
            if value > 0 and \
                    (not key.startswith('torch.legacy')):  # https://github.com/akmtn/pytorch-siggraph2017-inpainting/issues/2
                result.add(key)

        # 有的 api 可能已经失效了
        result1 = set()
        for module_name in result:
            try:
                print(module_name)
                module = locate(module_name)
                name = f'{module.__module__}.{module_name.split(".")[-1]}'
                # eg: torch.multiprocessing.Process.__init__；torch.jit._state._jit_caching_layer.clear
                # 有的 api 兜兜转转是别人的模块
                if name.startswith('torch'):
                    result1.add(name)
            except Exception as e:
                print(f"!!!!!!4 {e} {module_name=}")

            # TODO: del
            if module is None:
                continue

    print(result1 - result0)
    print(list(result1)[:5])
    print(list(result0)[:5])
    print('原始的使用 API', len(result))
    print('爬取的定义 API', len(result0))
    print('去除无效等 API', len(result1))
    print(len(result0 - result1))
    print(len(result1 - result0))
