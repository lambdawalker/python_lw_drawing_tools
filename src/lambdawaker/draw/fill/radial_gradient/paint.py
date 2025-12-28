from typing import Tuple, Union, Optional

import numpy as np
from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.fill.radial_gradient.parameters import generate_random_radial_gradient_parameters
from lambdawaker.random.values import Random, Default, clean_passed_parameters


def paint_radial_gradient(
        image: Image.Image,
        right_corner: Tuple[int, int] = (0, 0),
        size: Optional[Tuple[int, int]] = None,
        start_color: ColorUnion = (255, 255, 255, 255),
        end_color: ColorUnion = (0, 0, 0, 255),
        center: Optional[Tuple[float, float]] = None,
        radius: Optional[float] = None,
) -> None:
    """
    Draws a radial gradient onto an existing PIL image at a specific location.
    Modifies the original image in-place.
    """
    start_rgba = to_hsluv_color(start_color).to_rgba()
    end_rgba = to_hsluv_color(end_color).to_rgba()

    width, height = size if size is not None else image.size
    mode = image.mode

    # Default center to the middle of the area
    if center is None:
        cx, cy = width / 2.0, height / 2.0
    else:
        cx, cy = center

    # Default radius to cover the farthest corner
    if radius is None:
        corners = np.array([(0, 0), (width, 0), (width, height), (0, height)])
        distances = np.sqrt(((corners - np.array([cx, cy])) ** 2).sum(axis=1))
        max_radius = distances.max()
    else:
        max_radius = radius

    y, x = np.ogrid[:height, :width]
    dist_from_center = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)

    # Normalize distance to [0, 1] based on radius
    mask = dist_from_center / max_radius
    mask = np.clip(mask, 0, 1)
    mask = mask[..., np.newaxis]

    channels = 4 if mode == "RGBA" else 3
    start_c = np.array(start_rgba[:channels])
    end_c = np.array(end_rgba[:channels])

    # Interpolate: start_color at center (mask=0), end_color at radius (mask=1)
    gradient_array = (start_c + mask * (end_c - start_c)).astype(np.uint8)

    gradient_patch = Image.fromarray(gradient_array, mode=mode)

    # Use the patch itself as a mask if it has alpha,
    # ensuring it respects transparency during the paste
    image.paste(gradient_patch, right_corner, mask=gradient_patch if mode == "RGBA" else None)


def paint_random_radial_gradient(
        img: Image.Image,
        right_corner: Union[Tuple[int, int], Default, Random] = Default,
        size: Union[Tuple[int, int], Default, Random] = Default,
        start_color: Optional[ColorUnion] = None,
        end_color: Optional[ColorUnion] = None,
        center: Optional[Tuple[float, float]] = None,
        radius: Optional[float] = None,
) -> None:
    passed_values = clean_passed_parameters({
        "right_corner": right_corner,
        "size": size,
        "start_color": start_color,
        "end_color": end_color,
        "center": center,
        "radius": radius,
    })

    parameters = generate_random_radial_gradient_parameters(img, right_corner, size)

    parameters = parameters | passed_values
    paint_radial_gradient(img, **parameters)
