import random


def identify_scalar_type(element):
    scalar_type_name = type(element).__name__
    if scalar_type_name in ("bool", "int", "float"):
        return scalar_type_name
    raise ValueError(f"Unknown [{scalar_type_name}] type error")


def identify_value(value):
    value_type_name = type(value).__name__
    sub_value_type_name = None

    if value_type_name in ("list", "tuple"):
        if len(value) == 0:
            raise ValueError("Can't determine subtype")

        sub_value_type_name = identify_scalar_type(value[0])
    else:
        value_type_name = identify_scalar_type(value)

    return value_type_name, sub_value_type_name


def safe_get_from_list(lst, index):
    if lst is None:
        return None
    try:
        return lst[index]
    except IndexError:
        return None


def generate_random_scalar(value_type, value_range=None):
    if value_type == 'float':
        if value_range is not None:
            return random.uniform(value_range[0], value_range[1])  # Generates a random float within the given range
        else:
            return random.uniform(0.0, 100.0)  # Default range for random float
    elif value_type == 'int':
        if value_range is not None:
            return random.randint(value_range[0], value_range[1])  # Generates a random integer within the given range
        else:
            return random.randint(0, 100)  # Default range for random integer
    elif value_type == 'boolean':
        return random.choice([True, False])  # Generates a random boolean value
    else:
        raise ValueError("Unsupported value type. Choose from 'float', 'int', or 'boolean'.")


def generate_random_vector(vector_type, sub_value_type, length=None, value_ranges=None):
    if value_ranges is not None and length is None:
        length = len(value_ranges)

    if length is None:
        length = 4

    if vector_type == 'list':
        return [
            generate_random_scalar(
                sub_value_type,
                safe_get_from_list(value_ranges, i)
            )
            for i in range(length)
        ]
    elif vector_type == 'tuple':
        return tuple(
            generate_random_scalar(
                sub_value_type,
                safe_get_from_list(value_ranges, i)
            )
            for i in range(length)
        )
    else:
        raise ValueError(f"Unsupported [{vector_type}] type. Choose from 'list' or 'tuple'.")


def generate_random_value(value_type, sub_value_type=None, default_value=None, length=None, value_range=None):
    scalar_types = ['float', 'int', 'boolean']
    vector_types = ['list', 'tuple']

    if value_type in scalar_types:
        return generate_random_scalar(value_type, value_range)
    elif value_type in vector_types:
        length = length if length is not None else len(default_value)
        return generate_random_vector(value_type, sub_value_type, length, value_range)
    else:
        raise ValueError("Unsupported value type. Choose from 'float', 'int', 'boolean', 'list', or 'tuple'.")
