import random
from typing import Tuple, Union, Dict, Any

from PIL import Image

from lambdawaker.draw.color.generate_color import generate_hsluv_text_contrasting_color
from lambdawaker.draw.color.utils import get_random_point_with_margin
from lambdawaker.random.values import DefaultValue, Default, Random


def generate_random_hexagon_grid_parameters(
        img: Image.Image,
        size: Union[Tuple[int, int], Default, Random] = Default
) -> Dict[str, Any]:
    color = generate_hsluv_text_contrasting_color()

    if size is Default:
        size = DefaultValue(lambda: img.size)

    return {
        "area_size": get_random_point_with_margin(img.size, default=size, margin=0),
        "hexagon_size": random.uniform(10, 100),
        "thickness": random.uniform(1, 5),
        "angle": random.uniform(0, 360),
        "color": color,
    }
