import io

from PIL import Image
import numpy as np


class RawImage:
    def __init__(self, raw_data, mime_type):
        self.raw_data = raw_data
        self.mime_type = mime_type

    def to_pil(self):
        if self.mime_type == 'image/svg+xml':
            try:
                import cairosvg
                png_data = cairosvg.svg2png(bytestring=self.raw_data)
                return Image.open(io.BytesIO(png_data))
            except (ImportError, Exception):
                # Fallback or re-raise if cairosvg is not available
                pass

        return Image.open(io.BytesIO(self.raw_data))

    def to_numpy(self):
        pil_img = self.to_pil()
        return np.array(pil_img)
