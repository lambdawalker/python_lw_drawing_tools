import random
from typing import Tuple, Union, Dict, Any

from PIL import Image

from lambdawaker.draw.color.generate_color import generate_hsluv_text_contrasting_color
from lambdawaker.draw.color.utils import get_random_point_with_margin
from lambdawaker.random.values import DefaultValue, Default, Random


def generate_random_triangle_grid_parameters(
        img: Image.Image,
        size: Union[Tuple[int, int], Default, Random] = Default
) -> Dict[str, Any]:
    """
    Generates random parameters for a triangle grid.

    Args:
        img (Image.Image): The image for which the grid parameters are being generated.
        size (Union[Tuple[int, int], Default, Random], optional): The size of the grid area.
            If Default, it defaults to the image size. If Random, a random point with no margin is chosen.
            Defaults to Default.

    Returns:
        Dict[str, Any]: A dictionary containing the generated grid parameters, including:
            - "area_size": The size of the grid area.
            - "size": The side length of the triangles.
            - "thickness": The thickness of the triangle edges.
            - "angle": The rotation angle of the grid in degrees (0-360).
            - "color": The color of the triangle edges (HSLuv).
    """
    color = generate_hsluv_text_contrasting_color()

    if size == Default:
        size = DefaultValue(lambda: img.size)

    return {
        "area_size": get_random_point_with_margin(img.size, default=size, margin=0),
        "size": random.uniform(10, 100),
        "thickness": random.uniform(1, 5),
        "angle": random.uniform(0, 360),
        "color": color,
    }
