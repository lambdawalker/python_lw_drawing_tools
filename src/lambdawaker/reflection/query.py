import inspect
import random
import re

from lambdawaker.reflection.load import load_submodules


def select_random_function_from_module(module, name_pattern=None):
    """
    Given a module, selects a random function from that module.

    Args:
        module: A Python module object
        name_pattern: Optional regexp pattern to filter functions by name

    Returns:
        A randomly selected function from the module

    Raises:
        ValueError: If no functions are found in the module
    """
    functions = [obj for name, obj in inspect.getmembers(module) if inspect.isfunction(obj)]

    if name_pattern is not None:
        pattern = re.compile(name_pattern)
        functions = [func for func in functions if pattern.search(func.__name__)]

    if not functions:
        raise ValueError(f"No functions found in module {module.__name__}")

    return random.choice(functions)


def select_random_function_from_module_and_submodules(module, name_pattern=None):
    """
    Given a module, selects a random function from that module or any of its submodules.

    Args:
        module: A Python module object
        name_pattern: Optional regexp pattern to filter functions by name

    Returns:
        A randomly selected function from the module or its submodules

    Raises:
        ValueError: If no functions are found in the module or its submodules
    """

    load_submodules(module)
    return _select_random_function_from_module_and_submodules(module, name_pattern)


def query_all_functions_from_module(module, pattern):
    all_functions = []

    # Get functions from the current module
    current_module_functions = [
        obj for name, obj in inspect.getmembers(module)
        if inspect.isfunction(obj) and pattern.search(name)
    ]

    all_functions.extend(current_module_functions)

    # Recursively get functions from submodules
    for name, obj in inspect.getmembers(module):
        if inspect.ismodule(obj) and obj.__name__.startswith(module.__name__ + '.'):
            try:
                all_functions.extend(query_all_functions_from_module(obj, pattern))
            except ValueError:
                # No functions in submodule, continue to next
                pass

    return all_functions


def _select_random_function_from_module_and_submodules(module, name_pattern=None):
    """
        Given a module, selects a random function from that module or any of its submodules.

        Args:
            module: A Python module object
            name_pattern: Optional regexp pattern to filter functions by name

        Returns:
            A randomly selected function from the module or its submodules

        Raises:
            ValueError: If no functions are found in the module or its submodules
        """
    pattern = None
    if name_pattern is not None:
        pattern = re.compile(name_pattern)

    all_functions = query_all_functions_from_module(module, pattern)

    if not all_functions:
        raise ValueError(f"No functions found in module {module.__name__} or its submodules")

    return random.choice(all_functions)
