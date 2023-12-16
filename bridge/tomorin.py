from bridge.config import admin_list, ban_dicts_path, config

from bridge.wrap_xml_adder import h
from bridge.decorator_maker import on_event, on_activator
from bridge.utils import rm_1_at, unescape_special_characters, escape_special_characters, rm_all_at, rm_all_xml, rm_perfix
from bridge.api_maker import new_api
from bridge.session_adder import SessionExtension, MessageExtension, Function



#         if '-h' in self.message.command.args or '帮助' in self.message.command.args:
#             def add_indentation(text):
#                 # 分割文本到单独的行
#                 lines = text.split('\n')
#                 # 给每行添加四个空格
#                 indented_lines = ['    ' + line for line in lines]
#                 # 将修改后的行合并回一个字符串
#                 indented_text = '\n'.join(indented_lines)
#                 return indented_text
#             cmd_name = config["bot"]["prefix"][0] + self.function.command_list[0]
#             other_name = ', '.join(self.function.command_list[1:])
#             if other_name != '':
#                 other_name = f'\n别名：{other_name}'
#             doc_ = ''
#             main_doc = add_indentation(self.function.doc.replace('    ', '').strip())
#             for k, v in actions.items():
#                 # 如果k不是字符串
#                 # if not isinstance(k, str):
#                 #     continue
#                 if v:
#                     if not v.__doc__:
#                         continue
#                     if not k:
#                         action_doc = v.__doc__.strip().replace('\n', '，').replace(' ', '')
#                         doc_ += f'    {cmd_name}    {action_doc}\n'
#                         continue
#                     action_doc = v.__doc__.strip().replace('\n', '，').replace(' ', '')
#                     doc_ += f'    {cmd_name} {k}    {action_doc}\n'
#             if doc_.endswith('\n'):
#                 doc_ = doc_[:-1]
#             eg_ = ''
#             if self.function.arg_examples:
#                 for example in self.function.arg_examples:
#                     eg_ += f'\n    {cmd_name} {example}'
#             qq = ''
#             if self.platform in ['qq', 'qqguild']:
#                 qq = '·\n'
#             say = '指令示例：\n' if doc_ != '' or eg_ != '' else ''
#             if doc_ == '' and eg_.startswith('\n'):
#                 eg_ = eg_.replace('\n', '', 1)
#             help_doc_processed = f'''{qq}指令: {cmd_name}
# {main_doc}{other_name}
# {say}{doc_}{eg_}
# '''
#             # print('doc_', doc_)
#             # print('eg_', eg_)
#             self.send(help_doc_processed)
#             return


# @staticmethod
# def command(cmd: (str, list) = None):
#     '''
#     当命令被触发时触发。以 create-message 为底层事件。
#     支持传入字符串列表作为多个触发词。
#     如果没有提供 cmd 参数，则使用装饰的函数名作为命令，且此时不会被help命令识别。
#     '''
#     def decorator(func):
#         # print(f"Function name: {func.__name__}")
#         # print(f"Function docstring: {func.__doc__}")
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             wrapper.enable_feature = True
#             # print(cmd)
#             # print()
#             try:
#                 session = args[0]
#                 # print('session', session)
#                 # if isinstance(session, dict):
#                 #     return False
#
#             except IndexError:
#                 # print('你 session 呢 IndexError')
#                 return False
#             if config['bot']['rm_at']:
#                 pure_message = rm_all_at(session.message.content)
#             for prefix in config['bot']['prefix']:
#                 if pure_message.startswith(prefix):
#                     pure_message = pure_message.replace(prefix, '', 1)
#                     break
#
#             if session.type != 'message-created':
#                 return False
#
#             # 判断是否传入了命令名
#             command_names = cmd if isinstance(cmd, (list, tuple)) else [cmd]
#             # 如果cmd是函数，或者没有提供cmd，则使用函数名
#             if callable(cmd) or cmd is None:
#                 command_names = [func.__name__]
#             # 给此函数添加自己的指令触发词列表
#             session.function = Function(command_names, '')
#
#             # 检查是否匹配任一命令名
#             for command_name in command_names:
#                 if pure_message.startswith(command_name + ' '):
#                     cmd_list = pure_message.split()
#                     command_args = cmd_list[1:]
#                     text = pure_message.replace(command_name, '', 1)
#                     if text.startswith(' '):
#                         text = text.replace(' ', '', 1)
#                     session.message.command = Command(command_name, command_args, text)
#                     return func(session)
#                 elif pure_message == command_name:
#                     session.message.command = Command(command_name, None, '', )
#                     return func(session)
#             else:
#                 session.message.command = Command(None, None, '', )
#                 return func(session)
#         return wrapper
#     # # 如果传入的 cmd 是函数，表示没有提供命令名，直接返回装饰器
#     if callable(cmd):
#         return decorator(cmd)
#     else:
#         return decorator  # 否则，返回装饰器函数


