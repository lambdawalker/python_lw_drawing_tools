import random
from typing import Tuple, Union, Dict, Any

from PIL import Image

from lambdawaker.draw.color.generate_color import generate_hsluv_text_contrasting_color
from lambdawaker.draw.color.utils import get_random_point_with_margin
from lambdawaker.random.values import DefaultValue, Default


def generate_random_linear_gradient_parameters(
        img: Image.Image,
        right_corner: Union[Tuple[int, int], DefaultValue] = Default,
        size: Union[Tuple[int, int], DefaultValue] = Default
) -> Dict[str, Any]:
    color = generate_hsluv_text_contrasting_color()

    if right_corner is Default:
        right_corner = DefaultValue((0, 0))

    if size is Default:
        size = DefaultValue(lambda: img.size)

    return {
        "right_corner": get_random_point_with_margin(img.size, default=right_corner, margin=0),
        "size": get_random_point_with_margin(img.size, default=size, margin=0),
        "angle": random.uniform(0, 360),
        "start_color": color,
        "end_color": color.random_shade(),
    }
