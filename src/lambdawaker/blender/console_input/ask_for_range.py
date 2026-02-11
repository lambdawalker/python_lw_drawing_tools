def parse_range_parameter(parameter: str):
    parameter = parameter.strip()
    if parameter == 'null':
        return None

    try:
        return int(parameter)
    except ValueError:
        try:
            return float(parameter)
        except ValueError:
            raise ValueError(f"Cannot parse '{parameter}' as int or float")


def parse_range(range_str: str, value_name="", min_value=None, max_value=None):
    range_str = range_str.strip()

    if range_str == "C":
        print("range -> [[0.0, 1.0], [0.0, 1.0], [0.0, 1.0], [0.0, 1.0]]")
        return [[0.0, 1.0], [0.0, 1.0], [0.0, 1.0], [0.0, 1.0]]

    elif range_str == "E":
        print("range -> [[0.0, 360.0], [0.0, 360.0], [0.0, 360.0], [0.0, 360.0]]")
        return [[0.0, 360.0], [0.0, 360.0], [0.0, 360.0], [0.0, 360.0]]

    elif range_str == "F01":
        print("range -> [0.0, 1.0]")
        return [0.0, 1.0]

    elif range_str == "S":
        return [min_value, max_value]

    elif range_str == "-h":
        return ask_for_range(value_name, True, min_value=min_value, max_value=max_value)

    parts = range_str.split(',')
    parsed_ranges = []

    for part in parts:
        part = part.strip()
        if part == 'null':
            parsed_ranges.append(None)
        elif part == 'f01':
            parsed_ranges.append([0.0, 1.0])
        elif part == 'e':
            parsed_ranges.append([0.0, 360.0])
        else:
            start, end = part.split('>')
            parsed_ranges.append(
                [parse_range_parameter(start), parse_range_parameter(end)]
            )

    if len(parsed_ranges) == 1:
        parsed_ranges = parsed_ranges[0]

    print(f"range -> {parsed_ranges}")
    return parsed_ranges


def ask_for_range(value_name, print_help=False, min_value=None, max_value=None, purpose=None):
    suggested_range = ""

    if min_value is not None or max_value is not None:
        suggested_range = f" [{min_value} > {max_value}]"

    purpose_message = f" Is a {purpose}" if purpose is not None else ""

    message = f"{value_name}{suggested_range}{purpose_message}. What is the range?:"

    if print_help:
        message = """    Full shortcuts:
        "C"   -> return [[0.0, 1.0], [0.0, 1.0], [0.0, 1.0], [0.0, 1.0]
        "E"   -> return [[0.0, 360.0], [0.0, 360.0], [0.0, 360.0], [0.0, 360.0]]
        "F01" -> return [0.0, 1.0]
    
    Partial shortcuts, example: null, 1 > null, f01, e -> returns [None, [1,None], [0.0, 1.0], [0.0, 360.0]]
        "null" -> adds None
        "e"    -> adds [0.0, 360.0]
        "f01"  -> adds [0.0, 1.0]
    
    Enter range: """

    range_str = input(message).strip()
    if range_str == "":
        return {
            "randomize": False,
        }

    try:
        parsed_range = parse_range(range_str, value_name, min_value=min_value, max_value=max_value)
    except:
        print("Input malformed. Try gain.")
        return ask_for_range(value_name, min_value=min_value, max_value=max_value)

    return {
        "randomize": True,
        "range": parsed_range
    }
