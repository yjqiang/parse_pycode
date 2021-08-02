import inspect
import pydoc
from typing import Any

import torch

from extract_defined_api.main import get_submodules, search_functions_and_classes, resolve_original, resolve_by_trying_everything
import utils


class API:
    def __init__(self, path_: str, data_: Any):
        self.data = data_
        self.path = path_


class ObjectAPI(API):
    """
    是 object 的样子
    """
    pass


class StrAPI(API):
    """
    是 string 的样子
    """
    pass


if __name__ == '__main__':
    ##########################################################################################################
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
                    try:
                        sub_module = resolve_by_trying_everything(submodule_name)  # 转成可以直接使用的模块而不是 string
                    except Exception as e:
                        # TODO: del
                        if "\'torch._C\' is not a package" in str(e) \
                                or "from 'torch.distributed.rpc'" in str(e):  # https://stackoverflow.com/questions/60257756/unable-to-import-torch-distributed-rpc
                            pass
                        else:
                            print('??????', submodule_name, parent_module, parent_module.__name__, e)
                        continue

                if sub_module.__name__.startswith('torch'):
                    cur_modules_result.add(sub_module)

        cur_modules_result -= modules  # 去重
        modules |= cur_modules_result
        new_modules = cur_modules_result

    print('-' * 100)
    ##########################################################################################################
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

    api_defined_api_result = []
    for belonging, name, value in funcs:  # type: str, Any
        api = ObjectAPI(f'{belonging.__name__}.{name}', value)
        api_defined_api_result.append(api)

    for belonging, name, value in classes:  # type: str, Any
        api = ObjectAPI(f'{belonging.__name__}.{name}', value)
        api_defined_api_result.append(api)

    for belonging, name, value in datas:    # type: str, Any
        # 这里使用 locate 的方法话，直接就把数据算出来了。。。，而不是得到 api
        # eg: torch.serialization.MAGIC_NUMBER
        api = StrAPI(f'{belonging.__name__}.{name}', value)
        api_defined_api_result.append(api)

    for module in modules:
        api = ObjectAPI(f'{module.__name__}', module)
        api_defined_api_result.append(api)

    # 测试可以正常找到
    # eg: torch.quantization.quantize_fx.Tuple 可以用 from torch.quantization.quantize_fx import Tuple 使用（虽然不会有 zz 这么干）
    # eg: torch.optim.adamw.AdamW 有 对应 API，但是用 resolve 查看 torch.optim.adamw.AdamW 是找不到的
    tmp = []
    for api in api_defined_api_result:
        try:
            resolve_by_trying_everything(api.path)
            tmp.append(api)
        except Exception as e:
            try:
                # eg: torch.autograd.gradcheck._prepare_input 在 torch/autograd/__init__.py 把  gradcheck 重定义了（cao）
                if not inspect.isfunction(resolve_original('.'.join(api.path.split('.')[:-1]))):
                    print(f'!CHECK_DEFINED_API_ERROR {type(api)} {api.path=} {api.data=} {e}')
                else:
                    pass
                    # print(api.path)
            except Exception as e:
                print(f'!CHECK_DEFINED_API_ERROR {type(api)} {api.path=} {api.data=} {e}')
    print('爬取的定义 API', len(api_defined_api_result), len(tmp))
    # !!!!!!
    api_defined_api_result = api_defined_api_result
    print('-' * 100)
    ##########################################################################################################
    # 过滤
    orig = utils.open_json('data/extract_comment_and_class/used_api.json')['statistics']

    str_defined_api_result = set([api.path for api in api_defined_api_result])
    print(len(str_defined_api_result), len(api_defined_api_result))
    # assert len(str_defined_api_result) == len(api_defined_api_result)

    str_using_api_result = set([path for path in orig])

    used_api_len = len(str_using_api_result)  # 当下爬取的 api 总数

    print('爬取的定义 API', len(str_defined_api_result))
    print('仓库在用的 API', len(str_using_api_result))

    # 1. 先用暴力匹配字符串的方法，匹配掉一部分
    str_using_api_result -= str_defined_api_result
    print('当前覆盖率', 1 - len(str_using_api_result) / used_api_len, len(str_using_api_result), used_api_len)

    # 2. 动态加载，匹配掉另一部分
    # eg: 抓取 torch 的时候，torch.nn.modules.Tanh
    # 但 torch.nn.Tanh 也可
    tmp = set()
    for using_api in str_using_api_result:
        try:
            module = resolve_by_trying_everything(using_api)
            for defined_api in api_defined_api_result:
                if module == defined_api.data:
                    # print(f'!OK {using_api=} {defined_api.path=} {module=}')
                    tmp.add(using_api)  # 认为该 API 已经有定义了
                    break
        except Exception as e:
            pass
    str_using_api_result -= tmp
    print('当前覆盖率', 1 - len(str_using_api_result) / used_api_len, len(str_using_api_result), used_api_len)

    # 3. 存在一些例如 torch.optim.optimizer.Optimizer.__init__ 的 API（谁写出来的这个 sb 玩意）
    api_defined_api_result_expanded = []
    for defined_api in api_defined_api_result:
        if inspect.isclass(defined_api.data):
            # print(defined_api.data, defined_api.path)
            for _, the_defined_object in inspect.getmembers(defined_api.data, inspect.isroutine):  # https://stackoverflow.com/questions/1911281/how-do-i-get-list-of-methods-in-a-python-class
                api_defined_api_result_expanded.append(the_defined_object)

    tmp = set()
    for using_api in str_using_api_result:
        try:
            the_using_object = resolve_by_trying_everything(using_api)
            if the_using_object in api_defined_api_result_expanded:
                tmp.add(using_api)  # 认为该 API 已经有定义了
        except Exception as e:
            pass
    str_using_api_result -= tmp
    print('当前覆盖率', 1 - len(str_using_api_result) / used_api_len, len(str_using_api_result), used_api_len)

    # 4. 失效
    tmp = set()
    for using_api in str_using_api_result:
        # https://github.com/akmtn/pytorch-siggraph2017-inpainting/issues/2
        if using_api.startswith('torch.legacy'):
            tmp.add(using_api)
    str_using_api_result -= tmp
    print('当前覆盖率', 1 - len(str_using_api_result) / used_api_len, len(str_using_api_result), used_api_len)
    print(str_using_api_result)
    # print([(api.path,) for api in api_defined_api_result])

    tmp = {}
    for using_api in str_using_api_result:
        name = '.'.join(using_api.split('.')[:2])
        tmp[name] = tmp.get(name, 0) + 1

    print({key: value for key, value in tmp.items() if value > 5})
