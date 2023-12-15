
from bridge.session_adder import SessionExtension
from session_utils import show_session_log, show_session_data
from load_plugins import plugin_loader
from session_filter import ban_manager
import threading
import copy


def main(data):
    # 展示data
    # show_session_data(data)
    session = SessionExtension(data)
    # 控制台输出
    try:
        show_session_log(session)
        pass
    except Exception as e:
        print(f'[Error] Session 抛出 {e}')

    for k, v in plugin_loader.loaded_plugins.items():
        # 对 session 进行深度复制
        if ban_manager.check_before_plugin(session, v.__name__):
            session_copy = copy.deepcopy(session)

            # 使用 session 的副本创建并启动插件线程
            plugin_thread = threading.Thread(target=v, args=(session_copy,))
            plugin_thread.start()







