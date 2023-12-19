import re
import json
from config import config
from datetime import datetime
import time

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