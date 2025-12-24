import math
from typing import List

import aggdraw
from PIL import Image, ImageFont
from PIL import ImageDraw

from lambdawaker.draw.color.HSLuvColor import HSLuvColor, ColorUnion, to_hsluv_color
from lambdawaker.draw.color.generate_color import generate_hsluv_text_contrasting_color


def display_colors(hsl_colors: List[ColorUnion], square_size: int = 150, padding: int = 25, font_size: int = 14) -> Image.Image:
    """Display a list of colors as squares with HSL labels and 'a a' text inside.

    Args:
        hsl_colors (list): List of HSL color tuples, e.g., [(120, 50, 50), (240, 75, 60)] or HSLuvColor objects.
        square_size (int): Size of each color square in pixels.
        padding (int): Padding between squares in pixels.
        font_size (int): Font size for the HSL label text.

    Returns:
        PIL.Image.Image: The generated image showing all colors.
    """
    num_colors = len(hsl_colors)

    # Calculate grid dimensions (try to make it roughly square)
    cols = math.ceil(math.sqrt(num_colors))
    rows = math.ceil(num_colors / cols)

    # Calculate image dimensions
    label_height = font_size + 10
    total_square_height = square_size + label_height
    width = cols * (square_size + padding) + padding
    height = rows * (total_square_height + padding) + padding

    # Create image
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = aggdraw.Draw(img)

    # Try to load a default font
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
        letter_font = ImageFont.truetype("arial.ttf", square_size // 4)
    except:
        font = ImageFont.load_default()
        letter_font = ImageFont.load_default()

    for idx, color in enumerate(hsl_colors):
        color = to_hsluv_color(color)
        row = idx // cols
        col = idx % cols

        # Calculate position
        x = col * (square_size + padding) + padding
        y = row * (total_square_height + font_size * 1.3) + font_size * 1.3

        print(color)
        (h, s, l) = color
        # Convert HSL to RGB
        r, g, b, a = color.to_rgba()

        # Draw colored square
        brush = aggdraw.Brush((r, g, b, 255))
        pen = aggdraw.Pen((0, 0, 0, 255), 1)
        draw.rectangle((x, y, x + square_size, y + square_size), pen, brush)

        # Flush to apply square before drawing text
        draw.flush()

        # Calculate text positions for the two 'a' letters
        letter_spacing = square_size // 5
        white_x = x + square_size // 2 - letter_spacing - square_size // 16
        black_x = x + square_size // 2 + letter_spacing // 2
        text_y = y + square_size // 2 - square_size // 8

        text_draw = ImageDraw.Draw(img)

        # Draw white 'a'
        text_draw.text((white_x, text_y), 'a', fill=(255, 255, 255), font=letter_font)

        # Draw black 'a'
        text_draw.text((black_x, text_y), 'a', fill=(0, 0, 0), font=letter_font)

        # Draw HSL label below the square
        hsl_text = f"HSL({int(h)}, {int(s)}%, {int(l)}%)"
        label_y = y + square_size + 5
        text_draw.text((x, label_y), hsl_text, fill=(0, 0, 0), font=font)

        tag = f"{color.tag}"
        tag_y = label_y + 5 + font_size
        text_draw.text((x, tag_y), tag, fill=(0, 0, 0), font=font)

        # Reinitialize aggdraw context
        draw = aggdraw.Draw(img)

    draw.flush()
    return img


if __name__ == "__main__":
    # Test with a variety of HSL colors
    color = generate_hsluv_text_contrasting_color()

    test_colors = [
        color,
        color.random_shade(),
        color.complementary_color()
    ] + list(color.triadic_colors()) + list(color.analogous_colors())

    # Generate the color visualization
    result_image = display_colors(test_colors, square_size=150, padding=25, font_size=14)

    # Display the image (if running in an environment that supports it)
    result_image.show()
