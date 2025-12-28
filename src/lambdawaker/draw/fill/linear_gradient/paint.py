from typing import Tuple, Union

import numpy as np
from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.fill.linear_gradient.parameters import generate_random_linear_gradient_parameters
from lambdawaker.random.values import Random, Default, clean_passed_parameters


def paint_linear_gradient(
        image: Image.Image,
        right_corner: Tuple[int, int] = (0, 0),
        size: Tuple[int, int] = None,
        start_color: ColorUnion = (0, 0, 0, 255),
        end_color: ColorUnion = (255, 255, 255, 255),
        angle: float = 0,
):
    """
    Draws a linear gradient onto an existing PIL image at a specific location.
    Modifies the original image in-place.
    """
    start_rgba = to_hsluv_color(start_color).to_rgba()
    end_rgba = to_hsluv_color(end_color).to_rgba()

    width, height = size if size is not None else image.size
    mode = image.mode

    y, x = np.ogrid[:height, :width]
    rad = np.deg2rad(angle)
    cos_a, sin_a = np.cos(rad), np.sin(rad)

    norm_x = (x - width / 2)
    norm_y = (y - height / 2)
    projection = norm_x * cos_a + norm_y * sin_a

    p_min, p_max = projection.min(), projection.max()
    mask = (projection - p_min) / (p_max - p_min) if p_max != p_min else projection
    mask = mask[..., np.newaxis]

    channels = 4 if mode == "RGBA" else 3
    start_c = np.array(start_rgba[:channels])
    end_c = np.array(end_rgba[:channels])

    gradient_array = (start_c + mask * (end_c - start_c)).astype(np.uint8)

    gradient_patch = Image.fromarray(gradient_array, mode=mode)
    image.paste(gradient_patch, right_corner, mask=gradient_patch if mode == "RGBA" else None)


def paint_random_linear_gradient(
        img: Image.Image,
        right_corner: Union[Tuple[int, int], Default, Random] = Default,
        size: Union[Tuple[int, int], Default, Random] = Default,
        start_color: ColorUnion = None,
        end_color: ColorUnion = None,
        angle: float = None,
):
    passed_values = clean_passed_parameters({
        "right_corner": right_corner,
        "size": size,
        "start_color": start_color,
        "end_color": end_color,
        "angle": angle,
    })

    random_parameters = generate_random_linear_gradient_parameters(img, right_corner, size)

    parameters = random_parameters | passed_values
    paint_linear_gradient(img, **parameters)
