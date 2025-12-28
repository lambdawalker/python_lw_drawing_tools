import random
from typing import Tuple, Union, Dict, Any

from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion
from lambdawaker.draw.color.generate_color import generate_hsluv_text_contrasting_color
from lambdawaker.draw.color.utils import get_random_point_with_margin
from lambdawaker.random.values import DefaultValue, Default, Random


def generate_random_concentric_polygons_parameters(
        img: Image.Image,
        color: Union[ColorUnion, Default, Random] = Default,
        size: Union[Tuple[int, int], Default, Random] = Default
) -> Dict[str, Any]:
    """
    Generates a dictionary of random parameters for drawing concentric polygons.

    Args:
        img (Image.Image): The image object, used to determine canvas size.
        color (Union[ColorUnion, Default, Random], optional): The color for the polygons.
                                                               If Default, it defaults to (0, 0, 0, 0).
                                                               If Random, a contrasting HSLuv color is generated.
                                                               Defaults to Default.
        size (Union[Tuple[int, int], Default, Random], optional): The desired size of the canvas for the polygons.
                                                                  If Default, it uses the image size. Defaults to Default.

    Returns:
        Dict[str, Any]: A dictionary containing various parameters for drawing concentric polygons,
                        such as canvas size, number of sides, rotation step, spacing, color, thickness, and fill opacity.
    """
    if color is Default:
        color = (0, 0, 0, 0)
    elif color is Random:
        color = generate_hsluv_text_contrasting_color()

    if size is Default:
        size = DefaultValue(lambda: img.size)

    return {
        "canvas_size": get_random_point_with_margin(img.size, default=size, margin=0),
        "sides": random.randint(3, 8),
        "rotation_step": random.uniform(0, 15),
        "spacing": random.uniform(10, 50),
        "color": color,
        "thickness": random.uniform(1, 5),
        "fill_opacity": random.randint(0, 50),
    }
