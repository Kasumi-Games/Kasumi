
import importlib
import inspect
import os
import threading

from session_filter import ban_manager
from bridge.session_adder import SessionExtension


class PluginLoader:
    def __init__(self):
        self.loaded_plugins = {}

    def load_plugins(self):
        # session = SessionExtension(data_nil)
        for folder in [d for d in os.listdir('./plugins') if os.path.isdir(os.path.join('./plugins', d)) and not d.startswith('__')]:
            # print(f'[load_plugins] 正在加载插件包 [{folder}]')
            module = importlib.import_module(f'plugins.{folder}.index')
            for name, obj in inspect.getmembers(module):
                #         # 1. 如果是函数
                if not (
                        inspect.isfunction(obj) and
                        # not name.startswith('_') and
                        obj.__module__ == f'plugins.{folder}.index'
                        # and inspect.getdoc(obj) is not None
                ):
                    continue
                # 这个语句是为了在「不是插件的函数」传递「session」时抛出异常时结束这本次导入
                if inspect.signature(obj).parameters:
                    try:
                        # 故意传递一个空的 session，在对应插件做了异常处理的情况下，这里不会抛出异常
                        obj()
                    except:
                        pass
                else:
                    # print(f'[load_plugins] [{folder}] 函数 [{obj.__name__}] 没有参数，跳过')
                    continue
                # print(obj.__name__)
                if not hasattr(obj, 'enable_feature'):
                    # print(obj.__name__, '没有 enable_feature 属性')
                    continue
                self.loaded_plugins[name] = obj
                self.loaded_plugins[name].__doc__ = inspect.getdoc(obj)
                print(f'[load_plugins] [{folder}] 加载插件 [{obj.__name__}]')

    def get_loaded_plugins_list(self):
        return self.loaded_plugins


plugin_loader = PluginLoader()







