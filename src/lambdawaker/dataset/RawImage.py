import io

from PIL import Image


class RawImage:
    def __init__(self, raw_data, mime_type):
        self.raw_data = raw_data
        self.mime_type = mime_type

    def to_pil(self):
        return Image.open(io.BytesIO(self.raw_data))
