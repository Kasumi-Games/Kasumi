import base64
import io
from typing import Union
from PIL import Image

from core.h import H


class HExtension(H):
    @staticmethod
    def qq_passive(param: str):
        return f'<passive passiveId="{param}" />'

    @staticmethod
    def image(param: Union[Image.Image, bytes, str]):
        if isinstance(param, Image.Image):
            with io.BytesIO() as output:
                param.save(output, format='PNG')
                image_binary = output.getvalue()
            # 将二进制数据转换为Base64编码
            encoded_image = base64.b64encode(image_binary).decode('utf-8')
            # 构建XML格式字符串
            return f'<image url="data:image/png;base64,{encoded_image}"/>'
        elif isinstance(param, bytes):
            encoded_image = base64.b64encode(param).decode('utf-8')
            return f'<image url="data:image/png;base64,{encoded_image}"/>'
        else:
            if str(param).startswith("http://") or str(param).startswith("https://"):
                return f'<image url="{param}"/>'


h = HExtension





