from enum import IntEnum
from typing import Union, Callable, Optional
import random

from core.session import Session, Message
from core.api import Api
from bridge.utils import rm_1_at, rm_all_at, rm_all_xml, rm_perfix, rm_perfix_or_empty
import inspect
import types


class Arg:
    def __init__(self, name: str = None, description: str = ''):
        self.name: str = name
        self.description: str = description


class Examples:
    def __init__(self, examples=None):
        if examples is None:
            examples = []
        self.list_all: list = examples

    def add(self, name: str = None, description: str = ''):  # 添加参数
        arg = Arg(name, description)
        self.list_all.append(arg)
        return self

    def output(self) -> list:
        return self.list_all


class Cutshort:
    def __init__(self, cutshort_dict=None):
        if cutshort_dict is None:
            cutshort_dict = {}
        self.cutshort_dict: dict = cutshort_dict

    def add(self, arg: Optional[str | tuple], cutshort: Optional[str | list] = None):  # 添加参数
        self.cutshort_dict[arg] = cutshort
        return self


class Command:
    def __init__(self, name: str = None, args: list = None, text: str = ''):
        self.name: str = name
        self.args: list = args
        self.text: str = text


class Function:
    def __init__(self, names: list = None, description: str = ''):
        self.names = names
        self.description: str = description
        self.cutshort: Optional[Cutshort] = Cutshort()
        self.examples: Optional[Examples] = Examples()
        # self.matched: str = ''
        self.func = None
        self.matched: bool = False

    def register(self, names: list = None, func: str = None):
        # print(id(self))
        if func is None:
            frame = inspect.currentframe()
            caller_frame = frame.f_back
            func = caller_frame.f_code.co_name
        self.names = names  # 暂时不需要
        self.func = func
        # print(f'[register] {self.names} -> {self.func}')
        return self


class MessageExtension(Message):
    def __init__(self, message_info: dict):
        super().__init__(message_info)
        self.command: Optional[Command] = Command()


class SessionExtension(Session):
    def __init__(self, body: dict):
        super().__init__(body)
        self.function: Optional[Function] = Function()
        self.message: Optional[MessageExtension] = MessageExtension(self.data.get('message', {}))
        self.get_all_help_msg: bool = False

        if '' == self.message.content and self.type == 'message-created':
            msg = "".join(element['attrs']['content'] for element in self.data['message']['elements'] if element['type'] == 'text')
            self.message.content = msg.strip()  # 空格不需要了
        # 随机一个seq
        self.seq = random.randint(0, 1000000000)

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

    def action(self, actions: Union[dict, Callable]):
        # 如果已经匹配，直接返回自身
        global str
        if self.function.matched:
            return self
        if self.get_all_help_msg:
            self.function.matched = True
            return self

        pure_msg = self.message.content
        pure_msg = rm_all_xml(pure_msg)
        pure_msg = rm_perfix_or_empty(pure_msg).strip()
        if pure_msg == '':
            # print('pure_msg == 空')
            return self

        command_name = pure_msg.split()[0]
        # print(f'command_name: {command_name}')
        # 删掉列表第一个
        command_args = pure_msg.split()[1:]
        # print(f'command_args: {command_args}')
        command_text = pure_msg.replace(command_name, '', 1).strip()
        # print(f'command_text: {command_text}')

        # 先检查cutshort
        if self.function.cutshort != {}:
            # print(pure_msg)
            # 下面的arg是参数，cutshort是缩写
            # 举例 arg 是 '结束游戏'，cutshort 是 'bzd'
            for arg, cutshort in self.function.cutshort.cutshort_dict.items():
                # print(f'正在检查缩写: {cutshort}')
                # print(f'pure_msg: {pure_msg}')
                # print(cutshort)
                # print(pure_msg)
                # print(cutshort == pure_msg)
                if cutshort is None:
                    if self.function.names[0]:
                        self.function.matched = True
                        # print(self.function.names)
                        self.message.command = Command(self.function.names[0], pure_msg.split(), pure_msg)  # cutshort导致了这里的args和text一样（消息里不存在指令名，所以参数和text就是pure_msg）
                        actions[arg](self)
                        return self
                    else:
                        self.message.command = Command(self.function.names[0], pure_msg.split(), pure_msg)
                        actions[None](self)
                elif isinstance(cutshort, str):
                    if str(cutshort) == pure_msg:
                        if self.function.names[0]:
                            self.function.matched = True
                            # print(self.function.names)
                            self.message.command = Command(self.function.names[0], pure_msg.split(), pure_msg)
                            actions[arg](self)
                            return self
                elif isinstance(cutshort, list):
                    # 如果cutshort是列表，则检查列表中的任一元素是否 == pure_msg
                    if any(item == pure_msg for item in cutshort):
                        # 如果匹配，则执行对应的函数
                        self.function.matched = True
                        self.message.command = Command(self.function.names[0], pure_msg.split(), pure_msg)
                        actions[arg](self)
                        return self

        for function_name in self.function.names:
            # print(f'正在检查命令名: {command_name}')
            # print(f'pure_message: {pure_message}')
            if pure_msg.startswith(function_name + ' '):
                # print(f'匹配到命令名: {function_name}')
                # print(f'command_text!: {command_text}')
                self.message.command = Command(command_name, command_args, command_text)
                break
            elif function_name == command_name:
                # print(f'匹配到命令名: {function_name}')
                self.message.command = Command(command_name, None, '')
                break
        else:
            # print('没有匹配到命令名')
            return self

        if not self.message.command.name:
            # print('没有命令名')
            return self

        # print(f'命令名: {self.message.command.name}')
        # 如果接受参数是函数对象，直接执行
        if callable(actions):
            self.function.matched = True
            actions(self)
            return self

        # None 为参数的情况
        if None in actions.keys() and self.message.command.args is None:
            self.function.matched = True
            actions[None](self)
            return self
        # 对应参数的情况
        if self.message.command.args:
            for arg, func in actions.items():
                # 如果arg是元组，则检查元组中的任一元素是否在self.message.command.args中
                if isinstance(arg, tuple):
                    if any(item in self.message.command.args for item in arg):
                        # 如果匹配，则执行对应的函数
                        self.function.matched = True
                        func(self)
                        return self
                # 如果arg是字符串，则直接检查是否匹配
                elif isinstance(arg, str):
                    if arg in self.message.command.args:
                        self.function.matched = True
                        func(self)
                        return self

        # -h 为参数的情况
        if '-h' in self.message.command.args or '帮助' in self.message.command.args:
            self.function.matched = True
            output = ''  # 用于存储输出的字符串
            if self.platform in ['qq']:
                output += '·\n'  # 在开头加上一个点

            output += f'指令：{self.function.names[0]}\n'  # 输出指令名

            # 如果有描述，输出描述
            output += '  ' + self.function.description + '\n' if self.function.description != '' else ''

            other_name = ', '.join(self.function.names[1:])
            if other_name != '':
                other_name = f'别名：{other_name}'  # 如果有别名，输出别名
            output += other_name + '\n' if other_name != '' else ''

            all_list = self.function.examples.output()  # 获取所有参数
            if all_list:  # 如果有参数，输出 “指令示例：”
                output += '指令示例：\n'

            for arg in all_list:  # 遍历所有参数
                if arg.name:
                    output += f'  {self.function.names[0]} {arg.name} => {arg.description}\n'
                else:
                    output += f'  {self.function.names[0]} => {arg.description}\n'
            if self.function.cutshort.cutshort_dict:
                output += '快捷调用：\n'
                for arg, cutshort in self.function.cutshort.cutshort_dict.items():
                    if isinstance(cutshort, str):
                        output += f'  {cutshort} => /{self.function.names[0]} {arg}\n'
                    elif isinstance(cutshort, list):
                        for item in cutshort:
                            output += f'  {item} => /{self.function.names[0]} {arg}\n'
                    if cutshort is None:
                        if arg is None:
                            output += f'  [任意输入] => /{self.function.names[0]} [任意输入]\n'
                        else:
                            output += f'  [任意输入] => /{self.function.names[0]} {arg}\n'

            output = output.strip()  # 去掉最后的换行符

            self.send(output)
            return self
        # 如果都没有匹配，准备下一次链式调用，返回自身
        return self

