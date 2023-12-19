import copy
import threading

from bridge.session import SessionExtension
from bridge.utils import show_session_log, show_session_data
from bridge.load_plugins import plugin_loader
from bridge.filter import ban_manager

function_info_list = []


def main(data):
    session = SessionExtension(data)
    # 控制台输出
    try:
        show_session_log(session)
        pass
    except Exception as e:
        print(f'[Error] 抛出 {e}')

    for k, v in plugin_loader.loaded_plugins.items():
        # 对 session 进行深度复制
        if ban_manager.check_before_plugin(session, v.__name__):
            session_copy = copy.deepcopy(session)

            # 使用 session 的副本创建并启动插件线程
            plugin_thread = threading.Thread(target=v, args=(session_copy,))
            plugin_thread.start()





