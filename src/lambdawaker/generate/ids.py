import secrets
import string


# =============================================================================
# THE MRZ GENERATOR 3000
#
# "Why did the MRZ string break up with the Database?"
# "Because he said she was too 'random', and she said he was too 'constrained'.
#  He wanted a long-term relationship, but she just wanted to stay under 30."
#
# "Also, they couldn't communicate... he spoke SQL, and she only spoke <<<<<<."
# =============================================================================

def generate_line_1():
    """Format: [AlphaNum(25-29)][Filler] to 30 chars"""
    alphabet = string.ascii_uppercase + string.digits
    first_part_len = secrets.choice(range(25, 30))
    random_seq = ''.join(secrets.choice(alphabet) for _ in range(first_part_len))
    return random_seq.ljust(30, '<')


def generate_line_2():
    """Format: [AlphaNum(18-25)][3 Letters][Filler][NumericID(1-4)] to 30 chars"""
    alpha_num = string.ascii_uppercase + string.digits
    letters = string.ascii_uppercase
    numbers = string.digits

    seq_len = secrets.choice(range(18, 26))
    num_id_len = secrets.choice(range(1, 5))

    seq_part = ''.join(secrets.choice(alpha_num) for _ in range(seq_len))
    letters_part = ''.join(secrets.choice(letters) for _ in range(3))
    num_id_part = ''.join(secrets.choice(numbers) for _ in range(num_id_len))

    # The 'Sponge' logic: filler soaks up the remaining space
    filler_needed = 30 - (len(seq_part) + len(letters_part) + len(num_id_part))
    return f"{seq_part}{letters_part}{'<' * filler_needed}{num_id_part}"


def generate_line_3():
    """Format: [[Name][SEP]] repeated 1-4 times, then padded to 30 chars"""
    alphabet = string.ascii_uppercase
    num_segments = secrets.choice(range(1, 5))

    parts = []
    current_len = 0
    for _ in range(num_segments):
        remaining_space = 30 - current_len
        if remaining_space < 4:
            break

        # Range safety check to avoid the 'Empty Sequence' IndexError
        upper_bound = min(11, remaining_space)
        if upper_bound <= 3:
            name_seg = ''.join(secrets.choice(alphabet) for _ in range(max(1, remaining_space - 1)))
        else:
            seg_len = secrets.choice(range(3, upper_bound))
            name_seg = ''.join(secrets.choice(alphabet) for _ in range(seg_len))

        parts.append(name_seg + '<')
        current_len += len(name_seg) + 1

    return "".join(parts).ljust(30, '<')


def get_complete_mrz():
    """The Grand Finale: 3 lines, 90 characters, 100% beauty."""
    return f"{generate_line_1()}\n{generate_line_2()}\n{generate_line_3()}"


if __name__ == "__main__":
    print(get_complete_mrz())
