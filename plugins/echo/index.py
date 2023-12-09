import time

from bridge.tomorin import on_event, on_activator, admin_list, h

import requests


@on_activator.command('echo')
def echo(session):
    """
    回声
    复读你的话
    """
    if session.command.args:
        # session.message_create(content=session.command.text)
        session.send(session.command.text)


@on_event.message_created
def echo2(session):
    """
    回声2
    复读你的话
    """
    if session.message.content.startswith('echo ') and session.user.id in admin_list:
        session.send(session.message.content[5:])




