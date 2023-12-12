from enum import IntEnum
from typing import Union, Optional
import re

from core.config import config
from core.session_maker import Session, User
from core.api import Api


class UserCommand:
    def __init__(self, name: str = '', args: list = None, text: str = ''):
        self.name: str = name
        self.args: list = args
        self.text: str = text


class Function:
    def __init__(self, doc: str = '', command_list: list = None, arg_examples: list = None):
        self.doc: str = doc
        self.command_list: list = command_list
        self.arg_examples: list = arg_examples


class SessionExtension(Session):
    def __init__(self, body: dict):
        super().__init__(body)
        self.user_command: UserCommand = UserCommand()
        self.function: Optional[Function] = None
        if '' == self.message.content and self.type == 'message-created':
            msg = "".join(element['attrs']['content'] for element in self.data['message']['elements'] if element['type'] == 'text')
            self.message.content = msg.strip()  # 空格不需要了
        self.seq = 0  # 将 seq 定义为实例属性

    def send(self, message_content: str):
        # 使用实例属性时，直接通过 self 访问

        if self.platform in ['qq', 'qqguild'] and '<passive id=' not in message_content:
            self.seq += 1  # 增加实例属性 seq 的值
            # print(f'[qq-shiter] 当前seq: {self.seq}')
            message_content = message_content + f'<passive id="{self.message.id}" seq="{self.seq}"/>'
            print(f'[ (qq-shiter) < 被动消息 > send -> {self.platform}: {self.channel.id} ] ')
        else:
            print(f'[ send -> {self.platform}: {self.channel.id} ] ')
        return Api.message_create(self, channel_id=self.channel.id or self.guild.id, content=message_content)

    def action(self, actions: dict):
        # 获取 action 所有的 func 的 docstring
        # 遍历参数，检查每个参数是否在 session.command.args 中
        if None in actions and self.user_command.args is None:
            actions[None](self)
            return
        if self.user_command.args:
            for arg, func in actions.items():
                # print(arg)
                if arg in self.user_command.args:
                    # 执行与参数对应的函数
                    func(self)
                    return
        if '-h' in self.user_command.args or '帮助' in self.user_command.args:
            def add_indentation(text):
                # 分割文本到单独的行
                lines = text.split('\n')
                # 给每行添加四个空格
                indented_lines = ['    ' + line for line in lines]
                # 将修改后的行合并回一个字符串
                indented_text = '\n'.join(indented_lines)
                return indented_text
            cmd_name = config["bot"]["prefix"][0] + self.function.command_list[0]
            other_name = ', '.join(self.function.command_list[1:])
            if other_name != '':
                other_name = f'\n别名：{other_name}'
            doc_ = ''
            main_doc = add_indentation(self.function.doc.replace('    ', '').strip())
            for k, v in actions.items():
                # 如果k不是字符串
                # if not isinstance(k, str):
                #     continue
                if v:
                    if not v.__doc__:
                        continue
                    if not k:
                        action_doc = v.__doc__.strip().replace('\n', '，').replace(' ', '')
                        doc_ += f'    {cmd_name}    {action_doc}\n'
                        continue
                    action_doc = v.__doc__.strip().replace('\n', '，').replace(' ', '')
                    doc_ += f'    {cmd_name} {k}    {action_doc}\n'
            if doc_.endswith('\n'):
                doc_ = doc_[:-1]
            eg_ = ''
            if self.function.arg_examples:
                for example in self.function.arg_examples:
                    eg_ += f'\n    {cmd_name} {example}'
            qq = ''
            if self.platform in ['qq', 'qqguild']:
                qq = '·\n'
            say = '指令示例：\n' if doc_ != '' or eg_ != '' else ''
            if doc_ == '' and eg_.startswith('\n'):
                eg_ = eg_.replace('\n', '', 1)
            help_doc_processed = f'''{qq}指令: {cmd_name}
{main_doc}{other_name}
{say}{doc_}{eg_}
'''
            # print('doc_', doc_)
            # print('eg_', eg_)
            self.send(help_doc_processed)
            return

        if True in actions and self.user_command.args is not None:
            actions[True](self)
            return


