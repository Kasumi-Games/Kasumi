import re
import json
from datetime import datetime
import time

from bridge.config import config


def escape_special_characters(message: str):
    # 替换特殊字符为转义字符
    message = message.replace('&', '&amp;')
    message = message.replace('"', '&quot;')
    message = message.replace('<', '&lt;')
    message = message.replace('>', '&gt;')
    return message


def unescape_special_characters(escaped_message: str):
    # 将转义字符替换回特殊字符
    escaped_message = escaped_message.replace('&quot;', '"')
    escaped_message = escaped_message.replace('&amp;', '&')
    escaped_message = escaped_message.replace('&lt;', '<')
    escaped_message = escaped_message.replace('&gt;', '>')
    return escaped_message


def rm_1_at(text):
    clean_text = re.sub(r'<at.*?>', '', text, count=1)  # 使用 count=1 只替换第一个匹配项
    return clean_text.strip()


def rm_all_at(text):
    clean_text = re.sub(r'<at.*?>', '', text)  # 使用 count=1 只替换第一个匹配项
    return clean_text.strip()


def rm_all_xml(text):
    clean_text = re.sub(r'<.*?>', '', text)  # 使用 count=1 只替换第一个匹配项
    return clean_text.strip()


def rm_perfix(text):
    for prefix in config['bot']['prefix']:
        if text.startswith(prefix):
            text = text.replace(prefix, '', 1)
            break
    return text.strip()


def rm_perfix_or_empty(text):
    for prefix in config['bot']['prefix']:
        if text.startswith(prefix):
            text = text.replace(prefix, '', 1)
            return text.strip()
    else:
        text = ''
        return text


def show_session_log(session):
    # 展示日志
    message_content = session.message.content

    html_tag_pattern = re.compile(r'<.*?>')
    # 将所有HTML标签替换为占位符
    cleaned_text = re.sub(html_tag_pattern, '[媒体消息]', message_content)
    cleaned_text = cleaned_text[0:15] + '...' if len(cleaned_text) > 15 else cleaned_text
    cleaned_text = cleaned_text.replace("\n", " ").replace("\r", " ")

    user = session.user.name + f'<{session.user.id}>'
    guild = session.guild.name + f'<{session.guild.id}>'
    channel = session.channel.name + f'<{session.channel.id}>'
    place = channel if channel == guild else guild + '->' + channel
    # 获取24小时制度当前时间
    msg_time = datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')
    if session.type != 'internal':
        print(f"| {msg_time} | [ {session.platform}: {place} ] < {session.type} >（ {user} ）{cleaned_text}")


def show_session_data(data: dict):
    if config['server']['reload']:
        pretty_json = json.dumps(data, indent=4, ensure_ascii=False)
        print(pretty_json)
