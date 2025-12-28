from typing import Tuple, Union, Optional

import numpy as np
from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.fill.cosin_gradient.parameters import generate_random_cosine_gradient_parameters
from lambdawaker.random.values import Random, Default, clean_passed_parameters


def paint_cosine_gradient(
        image: Image.Image,
        right_corner: Tuple[int, int] = (0, 0),
        size: Optional[Tuple[int, int]] = None,
        start_color: ColorUnion = (0, 0, 0, 255),
        end_color: ColorUnion = (255, 255, 255, 255),
        angle: float = 0,
        wavelength: float = 100.0,
) -> None:
    """
    Draws a cosine wave gradient onto an existing PIL image at a specific location.
    The gradient oscillates between start_color and end_color.
    """
    # 1. Convert colors to RGBA
    start_rgba = to_hsluv_color(start_color).to_rgba()
    end_rgba = to_hsluv_color(end_color).to_rgba()

    width, height = size if size is not None else image.size
    mode = image.mode

    # 2. Create the coordinate grid
    y, x = np.ogrid[:height, :width]
    rad = np.deg2rad(angle)
    cos_a, sin_a = np.cos(rad), np.sin(rad)

    # 3. Project coordinates onto the angle vector
    # We use x and y directly to determine the phase of the wave
    projection = x * cos_a + y * sin_a

    # 4. Calculate Cosine Wave mask
    # Cosine ranges from -1 to 1; we shift and scale it to 0.0 to 1.0
    wave = 0.5 * (np.cos(2 * np.pi * projection / wavelength) + 1)
    mask = wave[..., np.newaxis]

    # 5. Interpolate colors
    channels = 4 if mode == "RGBA" else 3
    start_c = np.array(start_rgba[:channels])
    end_c = np.array(end_rgba[:channels])

    # Broadcasting: (H, W, 1) * (C,)
    gradient_array = (start_c + mask * (end_c - start_c)).astype(np.uint8)

    # 6. Create patch and paste onto original image
    gradient_patch = Image.fromarray(gradient_array, mode=mode)

    # Use the patch itself as a mask if it has alpha,
    # ensuring it respects transparency during the paste
    image.paste(gradient_patch, right_corner, mask=gradient_patch if mode == "RGBA" else None)


def paint_random_cosine_gradient(
        img: Image.Image,
        primary_color: Union[ColorUnion, Random] = Random,
        right_corner: Union[Tuple[int, int], Default, Random] = Default,
        size: Union[Tuple[int, int], Default, Random] = Default,
        start_color: Optional[ColorUnion] = None,
        end_color: Optional[ColorUnion] = None,
        angle: Optional[float] = None,
        wavelength: Optional[float] = None
) -> None:
    passed_values = clean_passed_parameters({
        "right_corner": right_corner,
        "size": size,
        "start_color": start_color,
        "end_color": end_color,
        "angle": angle,
        "wavelength": wavelength,
    })

    parameters = generate_random_cosine_gradient_parameters(
        img, primary_color, right_corner, size
    )

    parameters = parameters | passed_values
    paint_cosine_gradient(img, **parameters)
