

from bridge.tomorin import on_activator, on_event, h, admin_list, rm_perfix, rm_all_at, rm_all_xml, rm_1_at, unescape_special_characters, escape_special_characters, SessionExtension
from core.load_plugins import plugin_loader


@on_event.message_created
def _help(session: SessionExtension):
    session.function.register(['帮助', 'help'])
    session.action(_help_a)


def _help_a(session: SessionExtension):
    print('[help] 读取所有插件')
    plugin_loader.load_plugins()
    plugin_loader.get_loaded_plugins_list()
    help_dict = {}
    for k, v in plugin_loader.loaded_plugins.items():
        session.message.content = '_-__--——__--__-==——_-----_=_-_--——__'
        session.get_all_help_msg = True
        v(session)
        if session.function.matched:
            help_dict[session.function.names[0]] = session.function.description
    if help_dict:
        help_msg = ''
        if session.platform in ['qq']:
            help_msg += '·\n'
        help_msg += '当前可发送的指令有:\n'
        for k, v in help_dict.items():
            help_msg += f'  {k}：{v}\n'
        help_msg = help_msg.strip() + '\n@kasumi /指令名 帮助 获取指令信息。'
        session.send(help_msg)
