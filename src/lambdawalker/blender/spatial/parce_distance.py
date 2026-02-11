def parse_distance(distance_str):
    units = {
        'mm': 0.001,
        'cm': 0.01,
        'm': 1.0,
        'km': 1000.0
    }
    for unit in units:
        if distance_str.endswith(unit):
            value = float(distance_str[:-len(unit)])
            return value * units[unit]
    raise ValueError(f"Unsupported unit in distance string: {distance_str}")
