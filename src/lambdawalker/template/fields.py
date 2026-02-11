from lambdawalker.draw.color.HSLuvColor import to_hsluv_color
from lambdawalker.generate.field.address import generate_road_name, generate_block_name, generate_address_number, generate_city_name, generate_state_name, generate_country_name
from lambdawalker.generate.field.firs_name import generate_first_name
from lambdawalker.generate.field.institutions import generate_voting_institution_name
from lambdawalker.generate.field.last_name import generate_last_name
from lambdawalker.generate.ids import generate_random_mrz
from lambdawalker.generate.numbers import generate_hex_string, generate_int, generate_left_just_number, generate_boolean, generate_float
from lambdawalker.generate.pseudo_text_generator import PseudoTextGenerator

from lambdawalker.generate.time import generate_date, year_as_number, day_as_number, month_as_number

field_generators = {

    "text": PseudoTextGenerator(),
    "name": {
        "first": generate_first_name,
        "last": generate_last_name
    },
    "random": {
        "hex": generate_hex_string,
        "number": generate_int,
        "float": generate_float,
        "lf_number": generate_left_just_number,
        "boolean": generate_boolean,
        "mrz": generate_random_mrz
    },
    "color": {
        "hsluv": to_hsluv_color
    },

    "time": {
        "date": generate_date,
        "year_as_number": year_as_number,
        "day_as_number": day_as_number,
        "month_as_number": month_as_number
    },
    "address": {
        "road": generate_road_name,
        "block": generate_block_name,
        "number": generate_address_number,
        "city": generate_city_name,
        "state": generate_state_name,
        "country": generate_country_name
    },
    "institution": {
        "voting": generate_voting_institution_name
    }
}
