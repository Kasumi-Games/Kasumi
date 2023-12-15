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
