from enum import IntEnum
from typing import Union, Optional
import re

from core.config import config
from core.session_maker import Session
from core.api import Api


class Command:
    def __init__(self, command_name, args, text):
        self.command_name: str = command_name
        self.args: list = args
        self.text: str = text


class SessionExtension(Session):
    def __init__(self, body: dict):
        super().__init__(body)
        self.command: Optional[Command] = None
        if '' == self.message.content and self.type == 'message-created':
            msg = "".join(element['attrs']['content'] for element in self.data['message']['elements'] if element['type'] == 'text')
            self.message.content = msg.replace(' ', '', 1) if msg.startswith(' ') else msg
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





