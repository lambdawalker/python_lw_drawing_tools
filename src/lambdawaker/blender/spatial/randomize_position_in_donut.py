import math
import random


def generate_random_polar(min_radius=0.0, variation=1.0):
    theta = random.uniform(0, 2 * math.pi)
    radius = random.uniform(min_radius, min_radius + variation)
    return radius, theta


def polar_to_cartesian(radius, theta):
    x = radius * math.cos(theta)
    y = radius * math.sin(theta)
    return x, y


def randomize_position_in_donut(min_radius=0.0, variation=1.0):
    radius, theta = generate_random_polar(min_radius=min_radius, variation=variation)
    return polar_to_cartesian(radius, theta)
