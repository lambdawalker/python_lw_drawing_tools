import hsluv
from typing import Tuple, Union, Iterator

from lambdawaker.draw.color.generate_from_color import compute_random_shade_color, compute_complementary_color, compute_triadic_colors, compute_analogous_colors, compute_equidistant_variants
from lambdawaker.draw.color.utils import clamp_hue, clamp, hsl_string_to_tuple


class HSLuvColor:
    """
    Represents a color in the HSLuv color space with support for range constraints and basic manipulation.
    """
    def __init__(self, hue: float, saturation: float, lightness: float,
                 h_range: Tuple[float, float] = (0, 360), s_range: Tuple[float, float] = (0, 100), l_range: Tuple[float, float] = (0, 100), tag: str = ""):
        """
        Initialize HSLuv with value constraints.

        Args:
            hue (float): The hue value (0-360).
            saturation (float): The saturation value (0-100).
            lightness (float): The lightness value (0-100).
            h_range (tuple): Min and max allowed values for hue.
            s_range (tuple): Min and max allowed values for saturation.
            l_range (tuple): Min and max allowed values for lightness.
            tag (str): An optional tag or label for the color.
        """
        self.h_range = (h_range[0] % 360, h_range[1] % 360)
        self.s_range = s_range
        self.l_range = l_range

        # Initialize and clamp values to range
        self.hue = clamp_hue(hue, self.h_range)
        self.saturation = clamp(saturation, s_range)
        self.lightness = clamp(lightness, l_range)
        self.tag = tag

    def add_hue(self, amount: float) -> 'HSLuvColor':
        """
        Returns a new HSLuvColor with the hue adjusted by the given amount.
        """
        # We calculate the new position and then apply the circular constraint
        hue = clamp_hue(self.hue + amount, self.h_range)
        return HSLuvColor(hue, saturation=self.saturation, lightness=self.lightness)

    def add_saturation(self, amount: float) -> 'HSLuvColor':
        """
        Returns a new HSLuvColor with the saturation adjusted by the given amount.
        """
        saturation = clamp(self.saturation + amount, self.s_range)
        return HSLuvColor(self.hue, saturation=saturation, lightness=self.lightness)

    def add_lightness(self, amount: float) -> 'HSLuvColor':
        """
        Returns a new HSLuvColor with the lightness adjusted by the given amount.
        """
        lightness = clamp(self.lightness + amount, self.l_range)
        return HSLuvColor(self.hue, saturation=self.saturation, lightness=lightness)

    def __sub__(self, other: Union[str, Tuple[float, float, float], 'HSLuvColor']) -> 'HSLuvColor':
        """
        Allows hsluv - "50H" syntax.
        Returns a new instance to keep with Python's immutable __sub__ convention,
        or modifies self if you prefer in-place.
        """
        corrected = other
        if isinstance(other, str):
            try:
                corrected = hsl_string_to_tuple(other)
            except (ValueError, IndexError):
                raise ValueError(f"Invalid format: {other}. Use format like '50H'.")

        corrected = -corrected[0], -corrected[1], -corrected[2]
        return self.__add__(corrected)

    def __add__(self, other: Union[str, Tuple[float, float, float], 'HSLuvColor']) -> 'HSLuvColor':
        """
        Allows hsluv + "50H" syntax.
        Returns a new instance to keep with Python's immutable __add__ convention,
        or modifies self if you prefer in-place.
        """
        corrected = other
        if isinstance(other, str):
            try:
                corrected = hsl_string_to_tuple(other)
            except (ValueError, IndexError):
                raise ValueError(f"Invalid format: {corrected}. Use format like '50H'.")

        if isinstance(corrected, (tuple, list, HSLuvColor)):
            new_h, new_s, new_l = self.hue, self.saturation, self.lightness
            new_h += corrected[0]
            new_s += corrected[1]
            new_l += corrected[2]
        else:
            raise NotImplemented

        return HSLuvColor(new_h, new_s, new_l, self.h_range, self.s_range, self.l_range)

    def __getitem__(self, index: int) -> float:
        """Allows access via color[0], color[1], color[2]"""
        if index == 0:
            return self.hue
        elif index == 1:
            return self.saturation
        elif index == 2:
            return self.lightness
        else:
            raise IndexError("HSLuv index out of range. Use 0 (H), 1 (S), or 2 (L).")

    def __iter__(self) -> Iterator[float]:
        """Allows unpacking: h, s, l = color_instance"""
        yield self.hue
        yield self.saturation
        yield self.lightness

    def __len__(self) -> int:
        return 3

    def to_rgb(self) -> Tuple[int, int, int]:
        """
        Converts the HSLuv color to an RGB tuple with values in the range [0, 255].
        """
        r, g, b = hsluv.hsluv_to_rgb((self.hue, self.saturation, self.lightness))
        return int(r * 255), int(g * 255), int(b * 255)

    def __repr__(self) -> str:
        return f"HSLuv(H={self.hue:.1f}, S={self.saturation:.1f}, L={self.lightness:.1f})"

    def random_shade(self, lightness_limit: int = 30, min_distance: int = 10) -> 'HSLuvColor':
        """Generates a random shade of this color."""
        return compute_random_shade_color(self, lightness_limit=lightness_limit, min_distance=min_distance)

    def complementary_color(self) -> 'HSLuvColor':
        """Returns the complementary color."""
        return compute_complementary_color(self)

    def triadic_colors(self, factor: float = 1 / 3) -> Tuple['HSLuvColor', 'HSLuvColor']:
        """Returns the triadic color variants."""
        return compute_triadic_colors(self, factor=factor)

    def analogous_colors(self, factor: float = 1 / 8) -> Tuple['HSLuvColor', 'HSLuvColor']:
        """Returns the analogous color variants."""
        return compute_analogous_colors(self, factor=factor)

    def equidistant_variants(self, factor: float) -> Tuple['HSLuvColor', 'HSLuvColor']:
        """Returns two color variants equidistant from this color's hue."""
        return compute_equidistant_variants(self, factor=factor)
