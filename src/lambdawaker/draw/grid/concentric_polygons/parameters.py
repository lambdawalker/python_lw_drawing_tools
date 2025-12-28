import random
from typing import Tuple, Union, Dict, Any

from PIL import Image

from lambdawaker.draw.color.generate_color import generate_hsluv_text_contrasting_color
from lambdawaker.draw.color.utils import get_random_point_with_margin
from lambdawaker.random.values import DefaultValue, Default


def generate_random_concentric_polygons_parameters(
        img: Image.Image,  # The image object, used to determine canvas size.
        size: Union[Tuple[int, int], DefaultValue, Any] = Default  # The size of the canvas. Can be a tuple (width, height), a DefaultValue object, or any other type.
) -> Dict[str, Any]:
    """
    Generates a dictionary of random parameters for drawing concentric polygons.

    Args:
        img (Image.Image): The image object, used to determine canvas size if 'size' is not explicitly provided.
        size (Union[Tuple[int, int], DefaultValue, Any], optional): The desired size of the canvas for the polygons.
                                                                     Can be a tuple (width, height), a DefaultValue object
                                                                     (which will default to the image size), or any other type.
                                                                     Defaults to Default, which means it will use the image size.

    Returns:
        Dict[str, Any]: A dictionary containing various parameters for drawing concentric polygons,
                        such as canvas size, number of sides, rotation step, spacing, color, thickness, and fill opacity.
    """
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
