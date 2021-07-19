import builtins
import inspect
import pkgutil
import sys
import pydoc
from typing import Any, Tuple

import torch


def _visiblename(name, the_all=None, obj=None) -> bool:
    """Decide whether to show documentation on a variable."""
    # Certain special names are redundant or internal.
    # XXX Remove __initializing__?
    if name in {'__author__', '__builtins__', '__cached__', '__credits__',
                '__date__', '__doc__', '__file__', '__spec__',
                '__loader__', '__module__', '__name__', '__package__',
                '__path__', '__qualname__', '__slots__', '__version__'}:
        return False
    # Private names are hidden, but special names are displayed.
    if name.startswith('__') and name.endswith('__'):
        return True
    # Namedtuples have public fields and methods with a single leading underscore
    if name.startswith('_') and hasattr(obj, '_fields'):
        return True
    if the_all is not None:
        # only document that which the programmer exported in __all__
        return name in the_all
    else:
        return True
        # return not name.startswith('_')  # 这里改了


def search_functions_and_classes(the_object) -> Tuple[list, list, list]:
    """
    详见 pydoc.HTMLDoc.docmodule；提取函数和类名
    :param the_object:
    :return:
    """
    try:
        the_all = the_object.__all__
    except AttributeError:
        the_all = None

    classes = []
    for key, value in inspect.getmembers(the_object, inspect.isclass):  # type: str, Any
        # if __all__ exists, believe it.  Otherwise use old heuristic.
        if (the_all is not None or
                (inspect.getmodule(value) or the_object) is the_object):
            if _visiblename(key, the_all, the_object):
                classes.append((the_object, key, value))

    funcs = []
    for key, value in inspect.getmembers(the_object, inspect.isroutine):  # type: str, Any
        # if __all__ exists, believe it.  Otherwise use old heuristic.
        if (the_all is not None or
                inspect.isbuiltin(value) or inspect.getmodule(value) is the_object):
            if _visiblename(key, the_all, the_object):
                funcs.append((the_object, key, value))

    data = []
    for key, value in inspect.getmembers(the_object, pydoc.isdata):  # type: str, Any
        if _visiblename(key, the_all, the_object):
            data.append((the_object, key, the_object))

    return funcs, classes, data


def _locate_original(path, forceload=False):
    """
    Locate an object by name or dotted path, importing as necessary.；参考 pydoc.locate
    """
    parts = [part for part in path.split('.') if part]
    module, n = None, 0
    while n < len(parts):
        nextmodule = pydoc.safeimport('.'.join(parts[:n+1]), forceload)
        if nextmodule:
            module, n = nextmodule, n + 1
        else:
            break
    if module:
        the_object = module
    else:
        the_object = builtins
    for part in parts[n:]:
        try:
            the_object = getattr(the_object, part)
        except AttributeError as e:
            raise ImportError(str(e))
    return the_object


def resolve_original(the_object_name: str):
    """
    比较标准的名字（不瞎鸡儿乱写尝试）；参考 pydoc.resolve
    根据名字 load 函数、类等
    :return:
    """
    try:
        return _locate_original(the_object_name, forceload=False)  # 从 pydoc.writedoc 扒出来的
    except (ImportError, pydoc.ErrorDuringImport) as e:
        raise e
    except Exception as e:
        raise e


def _locate_by_trying_everything(path, forceload=False):
    """Locate an object by name or dotted path, importing as necessary. 魔改自 pydoc 的 locate 函数"""
    parts = [part for part in path.split('.') if part]
    module, n = None, len(parts)
    while n > 0:  # 截取 parts 长度为 n 的前几个元素
        try:
            # print(module, n, '.'.join(parts[:n]))
            module = pydoc.safeimport('.'.join(parts[:n]), forceload)  # 失败为 None
        except Exception:
            # print('--------')
            pass
        if module:
            break
        n -= 1
    if module:
        the_object = module
    else:
        the_object = builtins
    # print(parts[n:], module, n)
    for part in parts[n:]:
        try:
            the_object = getattr(the_object, part)
        except AttributeError as e:
            raise ImportError(str(e))
    return the_object


def resolve_by_trying_everything(the_object_name: str):
    """
    瞎鸡儿乱写尝试
    根据名字 load 函数、类等
    :return:
    """
    try:
        return sys.modules.get(the_object_name, None) or _locate_by_trying_everything(the_object_name, forceload=False)
    except Exception as e:
        raise e
        # return _locate_by_trying_everything(the_object_name, forceload=True)


def get_submodules(the_object) -> list[tuple[str, Any]]:
    """
    pydoc.HTMLDoc.docmodule 处理这个；查看当前模块下面的子模块
    :param the_object:
    :return:
    """
    # https://docs.python.org/3.6/reference/import.html#__path__
    # If the module is a package (either regular or namespace), the module the_object’s __path__ attribute must be set.
    # Non-package modules should not have a __path__ attribute.
    if hasattr(the_object, '__path__'):
        result = []
        for importer, modname, ispkg in pkgutil.iter_modules(the_object.__path__):
            result.append((modname, None))
        result.sort()
    else:
        result = inspect.getmembers(the_object, inspect.ismodule)
    return result


def fullname(something):
    """
    参考 https://stackoverflow.com/questions/2020014/get-fully-qualified-class-name-of-an-object-in-python
    https://stackoverflow.com/questions/58108488/what-is-qualname-in-python
    :param something:
    :return:
    """
    # https://docs.python.org/3.6/reference/import.html#__path__
    # If the module is a package (either regular or namespace), the module the_object’s __path__ attribute must be set.
    # Non-package modules should not have a __path__ attribute.
    if hasattr(something, '__path__'):
        # https://stackoverflow.com/questions/11705055/get-full-package-module-name
        # __name__ always contains the full name of the module.
        return something.__name__

    module = something.__module__
    if module == 'builtins':
        return something.__qualname__  # avoid outputs like 'builtins.str'
    return f'{module}.{something.__qualname__}'


def main():
    print(torch.__path__)
    print(torch.functional.F.torch)
    print(torch)
    get_submodules(torch._C)
    search_functions_and_classes(torch._C)
    print(resolve_by_trying_everything('torch._C'))


if __name__ == "__main__":
    main()
