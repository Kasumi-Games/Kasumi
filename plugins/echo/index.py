
from bridge.tomorin import on_activator, on_event, h, admin_list, SessionExtension
from PIL import Image


@on_event.message_created
def _echo(session: SessionExtension):
    session.function.register(['123', '1233'])
    session.function.description = '123'
    session.action(
        {
            None: echo,
        }
    )


def echo(session: SessionExtension):
    # pil画一个红色的图片
    img = Image.new('RGB', (100, 100), (255, 0, 0))
    session.send(h.image(img))


