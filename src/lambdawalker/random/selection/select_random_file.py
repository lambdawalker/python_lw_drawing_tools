import os
import random
from importlib.resources.readers import MultiplexedPath
from pathlib import Path


def select_random_file(path=None, extension_filter=None):
    if isinstance(path, str):
        path = Path(path)
    elif isinstance(path, MultiplexedPath):
        for candidate in path._paths:
            if candidate.is_dir():
                path = candidate
                break

    extension_filter = extension_filter if extension_filter is not None else []
    options = [os.path.join(path, f) for f in os.listdir(path)]

    if len(extension_filter):
        options = [
            f for f in options
            if os.path.splitext(f) in extension_filter or os.path.isdir(f)
        ]

    option = random.choice(options)

    if os.path.isfile(option):
        return option

    return select_random_file(path=option)
